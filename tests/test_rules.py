from datetime import date
from decimal import Decimal
from sqlalchemy import select
from app.models import (School,Subject,AcademicYear,ClassGroup,CurriculumLine,Employee,
                        EmployeeSubject,Allocation,User,BonusPeriod,BonusAssessment)
from app.services import (bonus_rate,priority_rank,validate_allocation,distribution_preview,
                          bonus_cap_ok,bonus_fund_ok,used_rate)
import pytest


def test_823_rates():
    assert [bonus_rate(i) for i in [64,65,70,71,75,76,80,81,85,86,90,91,95,96,100]] == [0,10,10,15,15,20,20,25,25,30,30,35,35,40,40]
    assert bonus_rate(85,'psychologist')==15
    assert bonus_rate(86,'librarian')==20
    assert bonus_rate(95,scheme='music')==20
    assert bonus_rate(59,scheme='music')==0
    with pytest.raises(ValueError):bonus_rate(101)


def test_3271_priority_expired_documents():
    e=Employee(qualification='top',qualification_valid_until=date(2024,1,1),
               national_certificate=True,certificate_valid_until=date(2027,1,1),degree='higher',employment_type='main')
    assert priority_rank(e,today=date(2026,11,19))==1
    e.qualification_valid_until=date(2027,5,5)
    assert priority_rank(e,today=date(2026,11,19))==0
    e.employment_type='part_time'
    assert priority_rank(e,today=date(2026,11,19))==6


def test_3271_primary_qualification_and_rate(db):
    d=db.query(School).first()
    if not d:
        d=School(district_id=1,code='01',name='School');db.add(d);db.flush()
    year=db.query(AcademicYear).first();subject=db.query(Subject).first()
    cl=ClassGroup(school_id=d.id,year_id=year.id,grade=2,section='A',student_count=20,approved=True)
    db.add(cl);db.flush()
    line=CurriculumLine(class_id=cl.id,subject_id=subject.id,weekly_hours=10,groups=1,source_ref='133',verified=True)
    e1=Employee(school_id=d.id,full_name='Test teacher',degree='higher',primary_specialist=False)
    db.add_all([line,e1]);db.flush()
    e_subject=EmployeeSubject(employee_id=e1.id,subject_id=subject.id,primary_methodology=False)
    db.add(e_subject);db.flush()
    with pytest.raises(ValueError,match='metodikasi'):validate_allocation(db,line,e1,5)
    e1.primary_specialist=True
    validate_allocation(db,line,e1,5)
    author=db.query(User).first()
    a=Allocation(line_id=line.id,employee_id=e1.id,weekly_hours=5,created_by=author.id)
    db.add(a);db.flush()
    assert abs(used_rate(db,e1.id)-5/18)<0.001
    with pytest.raises(ValueError,match='mavjud soat'):validate_allocation(db,line,e1,6)


def test_fair_same_rank(db):
    d=School(district_id=1,code='02',name='School2')
    db.add(d);db.flush();y=db.query(AcademicYear).first();s=db.query(Subject).first()
    c=ClassGroup(school_id=d.id,year_id=y.id,grade=7,section='A',student_count=28,approved=True)
    db.add(c);db.flush()
    line=CurriculumLine(class_id=c.id,subject_id=s.id,weekly_hours=6,groups=1,verified=True)
    db.add(line);db.flush()
    for i in range(2):
        e=Employee(school_id=d.id,full_name=f'Teacher{i}',qualification='first',degree='higher')
        db.add(e);db.flush()
        db.add(EmployeeSubject(employee_id=e.id,subject_id=s.id))
    db.flush()
    p=distribution_preview(db,line)
    assert sorted(x['hours'] for x in p)==[3,3]


def test_823_fund_and_top_half(db):
    d=School(district_id=1,code='03',name='School3');db.add(d);db.flush();y=db.query(AcademicYear).first()
    p=BonusPeriod(school_id=d.id,year_id=y.id,name='2026',fund_limit=Decimal('100'))
    db.add(p);db.flush()
    emps=[]
    for i in range(3):
        e=Employee(school_id=d.id,full_name=f'Teacher{i}',staff_type='teacher',base_salary=100)
        db.add(e);db.flush();emps.append(e)
    assert bonus_cap_ok(db,p,emps[0].id,10)
    a=BonusAssessment(period_id=p.id,employee_id=emps[0].id,score=70,rate=10,amount=10,state='approved')
    db.add(a);db.flush()
    assert not bonus_cap_ok(db,p,emps[1].id,10)
    assert bonus_fund_ok(db,p,90)
    assert not bonus_fund_ok(db,p,91)


def test_workload_clears_with_new_academic_year(db):
    d=School(district_id=1,code='TWOYEARS',name='Multiyear School')
    db.add(d);db.flush();y1=db.query(AcademicYear).first()
    y2=AcademicYear(name='2027/2028',active=False);db.add(y2);db.flush()
    subject=db.query(Subject).first()
    e=Employee(school_id=d.id,full_name='Teacher',primary_specialist=True)
    db.add(e);db.flush()
    admin=db.query(User).first()
    c1=ClassGroup(school_id=d.id,year_id=y1.id,grade=5,section='A',student_count=30,approved=True)
    c2=ClassGroup(school_id=d.id,year_id=y2.id,grade=5,section='A',student_count=30,approved=True)
    db.add_all([c1,c2]);db.flush()
    l1=CurriculumLine(class_id=c1.id,subject_id=subject.id,weekly_hours=10,verified=True)
    l2=CurriculumLine(class_id=c2.id,subject_id=subject.id,weekly_hours=10,verified=True)
    db.add_all([l1,l2]);db.flush()
    db.add_all([Allocation(line_id=l1.id,employee_id=e.id,weekly_hours=10,created_by=admin.id),
                Allocation(line_id=l2.id,employee_id=e.id,weekly_hours=10,created_by=admin.id)])
    db.flush()
    assert used_rate(db,e.id,year_id=y1.id)==0.5
    assert used_rate(db,e.id,year_id=y2.id)==0.5
