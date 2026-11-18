"""3271 va 823 yuzasidan versiyalanishi va huquqshunos tasdiqlashi lozim bo'lgan hisoblash servislari."""
from collections import defaultdict
from datetime import date
from decimal import Decimal
from math import floor
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import (Employee, EmployeeSubject, Subject, Allocation, CurriculumLine,
                     ClassGroup, AcademicYear, HourChangeRequest, CouncilDecision, BonusAssessment,
                     BonusPeriod, AuditLog, User)

# 3271-son 15-bandning 2026-08-01 dan kuchga kirgan tahriridagi navbat.
# Retraining diplomida tegishli kategoriya/sertifikat bo'lsa o'sha pog'onaga chiqadi.
PRIORITY_LABELS = {
    'top': '1. Oliy malaka toifasi',
    'subject_certificate': '2. Fan bo‘yicha milliy/xalqaro sertifikat',
    'first': '3. Birinchi malaka toifasi',
    'second': '4. Ikkinchi malaka toifasi',
    'higher_none': '5. Oliy maʼlumotli, toifasiz',
    'retrained': '6. Qayta tayyorlash diplomi (ekvivalent ustuvorlik tekshiriladi)',
    'part_time': '7. O‘rindosh oliy maʼlumotli',
    'student_3plus': '8. Pedagogika yo‘nalishi 3+ kurs talabasi',
    'vocational_primary': '9. Boshlang‘ich sinf uchun professional maʼlumot',
    'manager': '10. Tegishli mutaxassislikdagi rahbar',
}
PRIORITY_ORDER = list(PRIORITY_LABELS)
WEEKLY_FULL_RATE = {'primary':18.0, 'secondary':20.0}
MAX_RATE = 1.5
TOL = 0.001

def valid(date_value, today=None):
    return date_value is None or date_value >= (today or date.today())

def priority_rank(employee: Employee, today=None):
    """Ekvivalent qayta tayyorlanganlar o'z tasdiqlangan toifasi bo'yicha ustuvor bo'ladi."""
    today = today or date.today()
    if employee.priority_basis in ('student_3plus','vocational_primary','manager'):
        return PRIORITY_ORDER.index(employee.priority_basis)
    if employee.employment_type == 'part_time':
        return PRIORITY_ORDER.index('part_time')
    if employee.qualification == 'top' and valid(employee.qualification_valid_until,today): return 0
    if employee.national_certificate and employee.certificate_valid_until and valid(employee.certificate_valid_until,today): return 1
    if employee.qualification == 'first' and valid(employee.qualification_valid_until,today): return 2
    if employee.qualification == 'second' and valid(employee.qualification_valid_until,today): return 3
    if employee.degree == 'higher' or employee.retraining_diploma: return 4
    return 8 if employee.degree == 'vocational' else 9

def qualified(db: Session, employee: Employee, line: CurriculumLine) -> bool:
    if employee.school_id != line.klass.school_id or not employee.active or employee.staff_type != 'teacher':
        return False
    es = db.scalar(select(EmployeeSubject).where(EmployeeSubject.employee_id==employee.id,
                                                     EmployeeSubject.subject_id==line.subject_id))
    if not es: return False
    if line.klass.grade <= 4 and not (employee.primary_specialist or es.primary_methodology):
        return False
    if employee.priority_basis == 'vocational_primary' and line.klass.grade > 4:
        return False
    return True

def used_rate(db: Session, employee_id: int, exclude_allocation: int | None=None, year_id: int|None=None) -> float:
    # Historical years must not count toward the active academic year's weekly workload.
    if year_id is None:
        active=db.scalar(select(AcademicYear).where(AcademicYear.active==True))
        year_id=active.id if active else None
    q=(select(Allocation).join(CurriculumLine).join(ClassGroup)
       .where(Allocation.employee_id==employee_id))
    if year_id is not None: q=q.where(ClassGroup.year_id==year_id)
    records=db.scalars(q).all()
    total=0.0
    for a in records:
        if a.id==exclude_allocation:continue
        total += a.weekly_hours/(18.0 if a.line.klass.grade<=4 else 20.0)
    return round(total,6)

def annual_workload_estimate(db:Session,employee_id:int,year_id:int|None=None)->float:
    """Equivalent annual work hours (weekly lesson+pedagogic workload times 43).
    Must be reconciled with individual annual work schedule before final tariff.
    """
    return round(used_rate(db,employee_id,year_id=year_id)*1548,2)

def hours_total(db: Session, line_id: int, exclude_allocation=None) -> float:
    hours=db.scalar(select(func.coalesce(func.sum(Allocation.weekly_hours),0)).where(Allocation.line_id==line_id,
                                           Allocation.id!=exclude_allocation if exclude_allocation else True))
    return float(hours or 0)

def validate_allocation(db, line, employee, hours, exclude_allocation=None):
    if hours <= 0 or round(hours*2)!=hours*2:
        raise ValueError('Soat 0 dan katta va 0.5 qadamda bo‘lishi kerak')
    if not line.verified or not line.klass.approved:
        raise ValueError('Avval sinf va fan setkasini tasdiqlang')
    if not qualified(db, employee, line):
        raise ValueError('O‘qituvchining fan/boshlang‘ich metodikasi hujjati yoki maktabi mos emas')
    if hours_total(db,line.id,exclude_allocation)+hours>line.total_hours+TOL:
        raise ValueError('Fan setkasidagi mavjud soat oshib ketmoqda')
    rate=used_rate(db,employee.id,exclude_allocation,year_id=line.klass.year_id)+hours/(18 if line.klass.grade<=4 else 20)
    if rate>MAX_RATE+TOL:
        raise ValueError(f'1.5 stavka bo‘yicha taxminiy limit oshadi: {rate:.2f}. 3271 17-bandning yillik hisobi alohida ham tekshirilishi kerak.')

def distribution_preview(db: Session, line: CurriculumLine):
    """Ustuvor guruhlar bo'yicha yarim soat qadamda teng taklif. Qaror EMAS."""
    remaining=round((line.total_hours-hours_total(db,line.id))*2)/2
    if remaining<=0: return []
    people=db.scalars(select(Employee).where(Employee.school_id==line.klass.school_id,Employee.active==True)).all()
    ranked=defaultdict(list)
    for emp in people:
        if qualified(db,emp,line):
            capacity=max(0.0,(MAX_RATE-used_rate(db,emp.id,year_id=line.klass.year_id))*(18 if line.klass.grade<=4 else 20))
            capacity=floor((capacity+1e-7)*2)/2
            if capacity>=0.5: ranked[priority_rank(emp)].append((emp,capacity))
    result=[]
    for rank in sorted(ranked):
        members=sorted(ranked[rank],key=lambda x:x[0].id)
        shares={e.id:0.0 for e,_ in members}
        while remaining>=0.5-TOL:
            choices=[(e,cap) for e,cap in members if shares[e.id]+0.5<=cap+TOL]
            if not choices: break
            # give next half-hour to the least-loaded member of SAME ranking group
            e,_=min(choices,key=lambda x:(shares[x[0].id],x[0].id))
            shares[e.id]+=0.5; remaining=round(remaining-0.5,2)
        for emp,_ in members:
            if shares[emp.id]>0: result.append({'employee':emp,'rank':rank+1,'hours':shares[emp.id]})
        if remaining<=TOL: break
    return result

def bonus_rate(score: float, staff_type='teacher', scheme='standard') -> int:
    if not 0<=score<=100: raise ValueError('Ball 0–100 oralig‘ida bo‘lishi kerak')
    if scheme=='music':
        for threshold,rate in [(95,20),(90,18),(85,16),(80,14),(75,12),(70,10),(65,8),(60,5)]:
            if score>=threshold: return rate
        return 0
    if staff_type in ('psychologist','librarian'):
        return 20 if score>=86 else 15 if score>=76 else 10 if score>=65 else 0
    for threshold,rate in [(96,40),(91,35),(86,30),(81,25),(76,20),(71,15),(65,10)]:
        if score>=threshold: return rate
    return 0

def bonus_cap_ok(db: Session, period: BonusPeriod, new_employee_id: int, new_rate: float, exclude_id=None) -> bool:
    # Teacher winners <= floor(50% teacher headcount), NOT top 50% of any arbitrary score distribution.
    teachers=db.scalars(select(Employee).where(Employee.school_id==period.school_id,
                                  Employee.staff_type=='teacher',Employee.active==True)).all()
    teacher_ids={x.id for x in teachers}
    if new_employee_id not in teacher_ids: return True
    awarded={a.employee_id for a in db.scalars(select(BonusAssessment).where(
        BonusAssessment.period_id==period.id,BonusAssessment.state=='approved')).all()
        if (exclude_id is None or a.id!=exclude_id) and a.employee_id in teacher_ids and a.rate>0}
    if new_rate>0: awarded.add(new_employee_id)
    return len(awarded)<=floor(len(teacher_ids)*0.5)

def bonus_fund_ok(db,period,amount,exclude_id=None):
    if Decimal(str(period.fund_limit or 0))<=0: return False
    existing=db.scalars(select(BonusAssessment).where(BonusAssessment.period_id==period.id,
                     BonusAssessment.state=='approved')).all()
    total=sum((Decimal(str(a.amount or 0)) for a in existing if a.id!=exclude_id),Decimal('0'))
    return total+Decimal(str(amount))<=Decimal(str(period.fund_limit))

def audit(db, actor: User|None, action: str, school_id=None, entity='', entity_id=None, details=''):
    db.add(AuditLog(actor_id=actor.id if actor else None,school_id=school_id,action=action,
                    entity=entity,entity_id=entity_id,details=str(details)[:4000]))
