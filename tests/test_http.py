from sqlalchemy import select
from app.models import School,User,ClassGroup,Subject,Employee,Allocation,CurriculumLine
from app.security import hash_password
from .conftest import login,csrf_on


def test_district_creates_school_and_admin(client,db):
    login(client,'district','district-test-password')
    token=csrf_on(client,'/district/schools')
    r=client.post('/district/schools',data={'csrf':token,'code':'001','name':'Test maktab','language':'uz'})
    assert r.status_code==200 and 'Test maktab' in r.text
    s=db.scalar(select(School).where(School.code=='001'))
    r=client.post(f'/district/schools/{s.id}/admin',data={'csrf':token,'username':'school1',
        'full_name':'Maktab admin','password':'school-admin-password'})
    assert r.status_code==200
    u=db.scalar(select(User).where(User.username=='school1'))
    assert u.school_id==s.id and u.role=='school_admin'
    assert client.get('/school/staff').status_code==403 # district can't access individual employees
    assert client.get('/bonus').status_code==403 # district must not interfere with 823


def test_school_flow_and_teacher_consent(client,db):
    s=School(district_id=1,code='A01',name='School A');db.add(s);db.flush()
    db.add(User(school_id=s.id,username='sa',full_name='School admin',
          password_hash=hash_password('school-admin-password'),role='school_admin',must_change_password=False))
    db.commit()
    login(client,'sa','school-admin-password')
    token=csrf_on(client,'/school/staff')
    for who,loginname in [('Teacher A','ta'),('Teacher B','tb')]:
        r=client.post('/school/staff',data={'csrf':token,'full_name':who,'username':loginname,
             'password':'teacher-test-password','staff_type':'teacher','degree':'higher',
             'primary_specialist':'true'})
        assert r.status_code==200,r.text[:300]
    people=db.scalars(select(Employee).where(Employee.school_id==s.id)).all()
    subject=db.scalar(select(Subject).where(Subject.code=='MAT'))
    for e in people:
        r=client.post(f'/school/staff/{e.id}/subject',data={'csrf':token,'subject_id':subject.id})
        assert r.status_code==200
    r=client.post('/school/classes',data={'csrf':token,'grade':3,'section':'A','student_count':28,'language':'uz'})
    assert r.status_code==200
    c=db.scalar(select(ClassGroup).where(ClassGroup.school_id==s.id))
    client.post(f'/school/classes/{c.id}/approve',data={'csrf':token})
    r=client.post('/school/grid',data={'csrf':token,'class_id':c.id,'subject_id':subject.id,
       'weekly_hours':4,'groups':1,'source_ref':'2026-133-ilova'})
    assert r.status_code==200
    line=db.scalar(select(CurriculumLine).where(CurriculumLine.class_id==c.id))
    r=client.post(f'/school/grid/{line.id}/verify',data={'csrf':token})
    assert r.status_code==200
    r=client.get(f'/school/allocations/preview/{line.id}')
    assert r.status_code==200 and 'Tavsiya' in r.text
    r=client.post('/school/allocations',data={'csrf':token,'line_id':line.id,
         'employee_id':people[0].id,'weekly_hours':4})
    assert r.status_code==200
    a=db.scalar(select(Allocation).where(Allocation.line_id==line.id))
    r=client.post('/school/council',data={'csrf':token,'number':'12','council_date':'2026-09-12',
        'document_ref':'bayonnoma12.pdf'})
    assert r.status_code==200
    from app.models import CouncilDecision
    decision=db.scalar(select(CouncilDecision).where(CouncilDecision.school_id==s.id))
    r=client.post(f'/school/allocations/{a.id}/approve',data={'csrf':token,'decision_id':decision.id})
    assert r.status_code==200 and a.state=='approved'
    client.post('/logout',data={'csrf':token})
    # Users created by school admin must change password first. Mark complete only for test.
    for u in db.scalars(select(User).where(User.school_id==s.id,User.role=='teacher')):
        u.must_change_password=False
    db.commit()
    login(client,'ta','teacher-test-password')
    token=csrf_on(client,'/me')
    assert '4.0' in client.get('/me').text
    r=client.post('/me/requests',data={'csrf':token,'source_id':a.id,'target_id':people[1].id,
        'request_type':'transfer','weekly_hours':2,'reason':'Darslarni o‘zaro kelishib o‘tkazish'})
    assert r.status_code==200
    from app.models import HourChangeRequest
    change=db.scalar(select(HourChangeRequest).where(HourChangeRequest.school_id==s.id))
    client.post('/logout',data={'csrf':token})
    login(client,'tb','teacher-test-password')
    token=csrf_on(client,'/me')
    r=client.post(f'/me/requests/{change.id}/consent',data={'csrf':token,'choice':'accept'})
    assert r.status_code==200 and change.recipient_consented
    client.post('/logout',data={'csrf':token})
    login(client,'sa','school-admin-password')
    token=csrf_on(client,'/school/requests')
    r=client.post(f'/school/requests/{change.id}/decide',data={'csrf':token,'action':'approve',
            'decision_id':decision.id,'manager_note':'Kengash qaroriga ko‘ra'})
    assert r.status_code==200, r.text[:500]
    assert change.status=='approved'
    assert sum(x.weekly_hours for x in db.scalars(select(Allocation).where(Allocation.line_id==line.id)))==4
    export=client.get('/school/allocations/export.csv')
    assert export.status_code==200 and 'Teacher A' in export.text
    assert 'attachment;' in export.headers['content-disposition']
    client.post('/logout',data={'csrf':token})
    login(client,'ta','teacher-test-password')
    token=csrf_on(client,'/me')
    # Entire remaining allocation can be transferred while preserving request FK history.
    client.post('/me/requests',data={'csrf':token,'source_id':a.id,'target_id':people[1].id,
        'request_type':'transfer','weekly_hours':2,'reason':'Qolgan yuklamani ham o‘tkazish'})
    changes=db.scalars(select(HourChangeRequest).where(HourChangeRequest.school_id==s.id)
                      .order_by(HourChangeRequest.id)).all()
    new_change=changes[-1]
    client.post('/logout',data={'csrf':token})
    login(client,'tb','teacher-test-password')
    token=csrf_on(client,'/me')
    client.post(f'/me/requests/{new_change.id}/consent',data={'csrf':token,'choice':'accept'})
    client.post('/logout',data={'csrf':token})
    login(client,'sa','school-admin-password')
    token=csrf_on(client,'/school/requests')
    assert client.post(f'/school/requests/{new_change.id}/decide',
         data={'csrf':token,'action':'approve','decision_id':decision.id}).status_code==200
    db.refresh(a)
    assert a.weekly_hours==0 and a.state=='superseded'
    assert new_change.source_allocation_id==a.id
    assert sum(x.weekly_hours for x in db.scalars(select(Allocation).where(Allocation.line_id==line.id)))==4


def test_cross_school_rejected(client,db):
    s1=School(district_id=1,code='S1',name='School 1');s2=School(district_id=1,code='S2',name='School 2')
    db.add_all([s1,s2]);db.flush()
    db.add(User(school_id=s1.id,username='s1',full_name='S1',role='school_admin',
          password_hash=hash_password('school-one-password'),must_change_password=False));db.commit()
    foreign=Employee(school_id=s2.id,full_name='Other teacher');db.add(foreign);db.commit()
    login(client,'s1','school-one-password')
    token=csrf_on(client,'/school/staff')
    r=client.post(f'/school/staff/{foreign.id}/subject',data={'csrf':token,'subject_id':1})
    assert r.status_code==404
