"""Integration tests for school-scoped features safely reused from darstaqsimot."""
import csv
import io
from sqlalchemy import select
from app.models import (School, User, Subject, ClassGroup, CurriculumLine,
                        Allocation, Employee)
from app.security import hash_password
from app.curriculum_matrix import school_curriculum_matrix
from .conftest import login, csrf_on


def school_login(client, db, school_code='S01', username='schoolA'):
    school = School(district_id=1, code=school_code, name='Maktab '+school_code)
    db.add(school); db.flush()
    db.add(User(school_id=school.id, username=username, full_name='Admin '+school_code,
                password_hash=hash_password('school-password-abc'),
                role='school_admin', must_change_password=False))
    db.commit()
    login(client, username, 'school-password-abc')
    return school


def test_batch_classes_are_tenant_scoped_and_drafts(client, db):
    school = school_login(client, db)
    token = csrf_on(client, '/school/classes')
    response = client.post('/school/classes/batch', data={
        'csrf': token, 'grade': 3, 'count': 3, 'student_count': 29, 'language': 'uz'})
    assert response.status_code == 200
    classes = list(db.scalars(select(ClassGroup).where(ClassGroup.school_id == school.id)).all())
    assert [(c.grade,c.section,c.student_count,c.approved) for c in classes] == [
        (3,'A',29,False), (3,'B',29,False), (3,'V',29,False)]
    # Duplicate-free addition creates D and E, not A and B twice.
    response = client.post('/school/classes/batch', data={
        'csrf': token, 'grade': 3, 'count': 2, 'student_count': 29, 'language': 'uz'})
    assert response.status_code == 200
    assert set(db.scalars(select(ClassGroup.section).where(ClassGroup.school_id == school.id)).all()) == {'A','B','V','G','D'}
    assert client.post('/school/classes/batch', data={'csrf': token, 'grade': 4, 'count': 11}).status_code == 400
    assert client.post('/school/classes/batch', data={'csrf': token, 'grade': 4, 'count': 1, 'language': 'hack'}).status_code == 400
    assert client.post('/school/classes/batch', data={'csrf': 'bad', 'grade': 4, 'count': 1}).status_code == 403
    assert len(db.scalars(select(ClassGroup).where(ClassGroup.school_id == school.id)).all()) == 5


def test_matrix_distinguishes_learning_group_and_allocated_hours(client, db):
    school = school_login(client, db)
    cls1 = ClassGroup(school_id=school.id, year_id=1, grade=3, section='A',
                       student_count=27, language='uz', approved=True)
    cls2 = ClassGroup(school_id=school.id, year_id=1, grade=6, section='B',
                       student_count=28, language='uz', approved=True)
    db.add_all([cls1,cls2]);db.flush()
    s1 = db.scalar(select(Subject).where(Subject.code=='MAT'))
    s2 = Subject(code='ENG',name='Ingliz tili',grades_from=1,grades_to=11)
    db.add(s2);db.flush()
    l1=CurriculumLine(class_id=cls1.id,subject_id=s1.id,weekly_hours=5,groups=1,
                      verified=True,source_ref='133-son')
    l2=CurriculumLine(class_id=cls2.id,subject_id=s2.id,weekly_hours=3,groups=2,
                      verified=True,source_ref='133-son')
    db.add_all([l1,l2]);db.flush()
    e=Employee(school_id=school.id,full_name='Teacher A');db.add(e);db.flush()
    adminuser=db.scalar(select(User).where(User.username=='schoolA'))
    db.add_all([Allocation(line_id=l1.id,employee_id=e.id,weekly_hours=3,
                           state='approved',created_by=adminuser.id),
                Allocation(line_id=l2.id,employee_id=e.id,weekly_hours=4,
                           state='draft',created_by=adminuser.id),
                Allocation(line_id=l2.id,employee_id=e.id,weekly_hours=6,
                           state='superseded',created_by=adminuser.id)])
    db.commit()
    data=school_curriculum_matrix(db,school.id,1)
    assert data['totals']['learning_hours']==8
    assert data['totals']['teacher_hours']==11
    assert data['totals']['allocated_hours']==7  # archived 6 excluded
    assert data['totals']['approved_hours']==3
    assert data['totals']['remaining_hours']==4
    assert data['totals']['primary_teacher_hours']==5
    assert data['totals']['upper_teacher_hours']==6
    assert data['totals']['grouped_lines']==1
    assert school_curriculum_matrix(db,school.id,1,grade=3)['totals']['teacher_hours']==5
    assert school_curriculum_matrix(db,school.id,1,grade=6)['totals']['teacher_hours']==6
    response=client.get('/school/matrix')
    assert response.status_code==200 and 'Sinf–fan–soat matritsasi' in response.text
    assert 'Ingliz tili' in response.text and '3-A' in response.text
    assert client.get('/school/matrix?grade=12').status_code==400
    csv_response=client.get('/school/matrix/export.csv')
    assert csv_response.status_code==200
    assert 'attachment;' in csv_response.headers['content-disposition']
    rows=list(csv.reader(io.StringIO(csv_response.content.decode('utf-8-sig'))))
    assert len(rows)==3 and 'Ingliz tili' in str(rows)


def test_matrix_never_leaks_other_schools_and_requires_school_admin(client,db):
    s1=school_login(client,db)
    s2=School(district_id=1,code='S02',name='Private School 2');db.add(s2);db.flush()
    cls=ClassGroup(school_id=s2.id,year_id=1,grade=11,section='Z',student_count=22,language='uz')
    db.add(cls);db.flush()
    sub=db.scalar(select(Subject).where(Subject.code=='MAT'))
    db.add(CurriculumLine(class_id=cls.id,subject_id=sub.id,weekly_hours=4,groups=1,
                          source_ref='OTHER_PRIVATE_TOKEN'));db.commit()
    response=client.get('/school/matrix')
    assert response.status_code==200
    assert 'OTHER_PRIVATE_TOKEN' not in response.text
    assert '11-Z' not in response.text
    assert 'OTHER_PRIVATE_TOKEN' not in client.get('/school/matrix/export.csv').text
    # District admins cannot access a school-specific workload view.
    token=csrf_on(client,'/school/classes')
    client.post('/logout',data={'csrf':token})
    login(client,'district','district-test-password')
    assert client.get('/school/matrix').status_code==403
    assert client.get('/school/matrix/export.csv').status_code==403
    assert client.post('/school/classes/batch',data={'grade':3,'count':1,'csrf':'missing'}).status_code==403


def test_spreadsheet_formula_escaping():
    from app.controllers.matrix import safe_csv
    for payload in ('=HYPERLINK("evil")','+SUM(A1:B2)','-2+3','@SUM(1,2)'):
        assert safe_csv(payload).startswith("'")
    assert safe_csv('Oddiy fan')=='Oddiy fan'
