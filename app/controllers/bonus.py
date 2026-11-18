from decimal import Decimal
from math import floor
from fastapi import APIRouter,Depends,Form,Request,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import (User,School,Employee,BonusPeriod,BonusAssessment,AcademicYear,BonusCriterion,BonusCriterionScore,BonusMeeting)
from ..security import current_user,require_role,check_csrf
from ..services import bonus_rate,bonus_fund_ok,bonus_cap_ok,audit
from ..ui import admin,page,back

router=APIRouter(prefix='/bonus')

def bonus_user(request,db):
    u=current_user(request,db)
    if u.must_change_password:raise HTTPException(403,'Avval parolingizni o‘zgartiring')
    require_role(u,'school_admin','bonus_committee')
    return u

def scoped_period(db,user,pid):
    p=db.get(BonusPeriod,pid)
    if not p or p.school_id!=user.school_id:raise HTTPException(404,'Ustama davri topilmadi')
    return p

@router.get('')
def bonuses(request:Request,db:Session=Depends(get_db)):
    u=bonus_user(request,db)
    y=db.scalar(select(AcademicYear).where(AcademicYear.active==True))
    periods=db.scalars(select(BonusPeriod).where(BonusPeriod.school_id==u.school_id)
                       .order_by(BonusPeriod.id.desc())).all()
    employees=db.scalars(select(Employee).where(Employee.school_id==u.school_id,Employee.active==True)
                         .order_by(Employee.full_name)).all()
    assessments=db.scalars(select(BonusAssessment).join(BonusPeriod).where(BonusPeriod.school_id==u.school_id)
                          .order_by(BonusAssessment.id.desc())).all()
    return page(request,'bonuses.html',db,periods=periods,employees=employees,assessments=assessments,
                teachers_count=len([e for e in employees if e.staff_type=='teacher']),year=y,
                meetings=db.scalars(select(BonusMeeting).join(BonusPeriod).where(BonusPeriod.school_id==u.school_id)).all())

@router.post('/periods')
def create_period(request:Request,name:str=Form(...),fund_limit:float=Form(...),
 group_member_count:int=Form(...),group_protocol:str=Form(...),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf)
    y=db.scalar(select(AcademicYear).where(AcademicYear.active==True))
    if not y:raise HTTPException(409,'Faol o‘quv yili yo‘q')
    if fund_limit<=0:raise HTTPException(400,'Jamg‘arma limiti 0 dan katta bo‘lishi kerak')
    # 823 10-band: kamida 7 kishidan iborat toq sonli guruh
    if group_member_count<7 or group_member_count%2!=1 or not group_protocol.strip():
        raise HTTPException(400,'Ishchi guruh kamida 7 nafar toq sondagi aʼzodan iborat bo‘lishi va bayonnoma mavjud bo‘lishi kerak')
    if db.scalar(select(BonusPeriod).where(BonusPeriod.school_id==u.school_id,
        BonusPeriod.year_id==y.id,BonusPeriod.name==name)):raise HTTPException(409,'Davr mavjud')
    p=BonusPeriod(school_id=u.school_id,year_id=y.id,name=name,
        fund_limit=Decimal(str(fund_limit)),group_member_count=group_member_count,group_protocol=group_protocol)
    db.add(p);db.flush();audit(db,u,'bonus.period.create',u.school_id,'bonus_period',p.id)
    db.commit();return back('/bonus','Ustama davri yaratildi')

@router.post('/assessments')
def add_assessment(request:Request,period_id:int=Form(...),employee_id:int=Form(...),
 score:float=Form(...),evidence:str=Form(...),scheme:str=Form('standard'),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=bonus_user(request,db);check_csrf(request,csrf)
    p=scoped_period(db,u,period_id)
    if p.status!='draft':raise HTTPException(409,'Davr yopilgan')
    e=db.get(Employee,employee_id)
    if not e or e.school_id!=u.school_id:raise HTTPException(404,'Xodim topilmadi')
    if e.staff_type not in ('teacher','psychologist','librarian'):
        raise HTTPException(400,'Rahbarlar KPI ustamalari alohida modulda rasmiylashtiriladi')
    if scheme not in ('standard','music'):raise HTTPException(400,'Noto‘g‘ri ustama turi')
    if scheme=='music' and e.staff_type!='teacher':raise HTTPException(400,'Cholg‘u ustamasi o‘qituvchilarga tegishli')
    if db.scalar(select(BonusAssessment).where(BonusAssessment.period_id==p.id,
          BonusAssessment.employee_id==e.id)):raise HTTPException(409,'Bu xodim baholangan')
    if not evidence.strip():raise HTTPException(400,'Tasdiqlovchi hujjat yoki bayonnoma ko‘rsating')
    try:rate=bonus_rate(score,e.staff_type,scheme)
    except ValueError as exc:raise HTTPException(400,str(exc))
    if Decimal(str(e.base_salary or 0))<=0:raise HTTPException(400,'Avval xodimning tekshirilgan bazaviy tarif stavkasini kiriting')
    amount=(Decimal(str(e.base_salary or 0))*Decimal(str(rate))/100).quantize(Decimal('0.01'))
    a=BonusAssessment(period_id=p.id,employee_id=e.id,score=score,evidence=('[scheme:'+scheme+'] '+evidence),
                      rate=rate,amount=amount)
    db.add(a);db.flush();audit(db,u,'bonus.assessment.create',u.school_id,'bonus_assessment',a.id)
    db.commit();return back('/bonus','Baholash kiritildi (loyiha)')

@router.post('/meetings')
def record_meeting(request:Request,period_id:int=Form(...),held_on:str=Form(...),
    protocol_ref:str=Form(...),attendees:int=Form(...),votes_for:int=Form(...),votes_against:int=Form(...),
    votes_abstain:int=Form(0),labor_union_present:bool=Form(False),parent_present:bool=Form(False),
    supervisory_board_present:bool=Form(False),director_order_ref:str=Form(...),
    csrf:str=Form(...),db:Session=Depends(get_db)):
    u=bonus_user(request,db);check_csrf(request,csrf);p=scoped_period(db,u,period_id)
    if p.status!='draft':raise HTTPException(409,'Davr yopilgan')
    from math import ceil
    from datetime import date
    if attendees<ceil(p.group_member_count*2/3) or attendees>p.group_member_count:
        raise HTTPException(400,'Kvorum: jami aʼzolarning kamida 2/3 qismi qatnashishi kerak')
    if not (labor_union_present and parent_present and supervisory_board_present):
        raise HTTPException(400,'Kasaba uyushmasi, kuzatuv kengashi va ota-ona vakillari qatnashishi shart')
    if any(n<0 for n in (votes_for,votes_against,votes_abstain)) or votes_for+votes_against+votes_abstain!=attendees:
        raise HTTPException(400,'Ovozlar yig‘indisi qatnashchilar soniga teng bo‘lishi kerak')
    if votes_for<=attendees//2 or not protocol_ref.strip() or not director_order_ref.strip():
        raise HTTPException(400,'Ko‘pchilikning ijobiy ovozi, bayonnoma va direktor buyrug‘i talab etiladi')
    try:d=date.fromisoformat(held_on)
    except ValueError:raise HTTPException(400,'Sana noto‘g‘ri')
    m=BonusMeeting(period_id=p.id,held_on=d,protocol_ref=protocol_ref,
       attendees=attendees,votes_for=votes_for,votes_against=votes_against,votes_abstain=votes_abstain,
       labor_union_present=labor_union_present,parent_present=parent_present,
       supervisory_board_present=supervisory_board_present,director_order_ref=director_order_ref,
       recorded_by=u.id)
    db.add(m);db.flush();audit(db,u,'bonus.meeting.record',u.school_id,'bonus_meeting',m.id)
    db.commit();return back('/bonus','Majlis bayonnomasi qayd etildi')

@router.post('/assessments/{aid}/approve')
def approve_assessment(aid:int,request:Request,meeting_id:int=Form(...),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=bonus_user(request,db);check_csrf(request,csrf)
    require_role(u,'bonus_committee') # School admin cannot unilaterally approve working group's decision.
    a=db.get(BonusAssessment,aid)
    if not a:raise HTTPException(404,'Baholash yo‘q')
    p=scoped_period(db,u,a.period_id)
    e=db.get(Employee,a.employee_id)
    if p.status!='draft' or a.state!='draft':raise HTTPException(409,'Baholashni tasdiqlab bo‘lmaydi')
    if p.group_member_count<7 or p.group_member_count%2!=1 or not p.group_protocol.strip():
        raise HTTPException(400,'Ishchi guruh bayonnomasi noto‘g‘ri')
    meeting=db.get(BonusMeeting,meeting_id)
    if not meeting or meeting.period_id!=p.id:
        raise HTTPException(400,'Ijobiy qaror qabul qilingan ishchi guruh majlisi kerak')
    if u.employee_id==a.employee_id:
        raise HTTPException(403,'Manfaatlar to‘qnashuvi: o‘zingizning ustamangizni tasdiqlay olmaysiz')
    if not bonus_cap_ok(db,p,e.id,a.rate,exclude_id=a.id):
        raise HTTPException(400,'823-son nizom: ustama oladigan pedagoglar jami pedagoglarning 50 foizidan oshmasligi kerak')
    if not bonus_fund_ok(db,p,a.amount,exclude_id=a.id):
        raise HTTPException(400,'Jamg‘armaning mablag‘ limiti oshadi')
    # Criterion scoring remains provisional: committee explicitly confirms evidence.
    a.state='approved';a.approved_by=u.id
    audit(db,u,'bonus.approve',u.school_id,'bonus_assessment',a.id,
          f'ball={a.score};rate={a.rate};amount={a.amount}')
    db.commit();return back('/bonus','Ishchi guruh aʼzosi tasdiqladi')

@router.post('/committee')
def create_committee_login(request:Request,name:str=Form(...),username:str=Form(...),password:str=Form(...),
                           csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf)
    from ..security import hash_password
    if db.scalar(select(User).where(User.username==username)):raise HTTPException(409,'Login band')
    try:hashed=hash_password(password)
    except ValueError as exc:raise HTTPException(400,str(exc))
    member=User(full_name=name,username=username,password_hash=hashed,school_id=u.school_id,
                role='bonus_committee',must_change_password=True)
    db.add(member);db.flush();audit(db,u,'bonus.committee.account',u.school_id,'user',member.id)
    db.commit();return back('/bonus','Ishchi guruh hisobiga kirish yaratildi')
