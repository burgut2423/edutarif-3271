from fastapi import APIRouter,Depends,Form,Request,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Allocation,Employee,ClassGroup,CurriculumLine,HourChangeRequest,BonusAssessment,BonusPeriod
from ..security import check_csrf
from ..services import used_rate,audit
from ..ui import teacher,page,back

router=APIRouter(prefix='/me')

@router.get('')
def my_hours(request:Request,db:Session=Depends(get_db)):
    u=teacher(request,db)
    assignments=db.scalars(select(Allocation).where(Allocation.employee_id==u.employee_id,
                        Allocation.state=='approved').order_by(Allocation.id.desc())).all()
    peers=db.scalars(select(Employee).where(Employee.school_id==u.school_id,Employee.id!=u.employee_id,
                                Employee.active==True,Employee.staff_type=='teacher')).all()
    pending=db.scalars(select(HourChangeRequest).where(
        (HourChangeRequest.requester_id==u.employee_id)|(HourChangeRequest.target_employee_id==u.employee_id))
        .order_by(HourChangeRequest.id.desc())).all()
    peer_allocations=db.scalars(select(Allocation).join(CurriculumLine).join(ClassGroup).where(
         ClassGroup.school_id==u.school_id,Allocation.employee_id!=u.employee_id,Allocation.state=='approved')).all()
    bonuses=db.scalars(select(BonusAssessment).join(BonusPeriod).where(
        BonusAssessment.employee_id==u.employee_id,BonusAssessment.state=='approved')).all()
    return page(request,'teacher.html',db,allocations=assignments,peers=peers,pending=pending,
                peer_allocations=peer_allocations,rate=used_rate(db,u.employee_id),bonuses=bonuses)

@router.post('/requests')
def make_request(request:Request,source_id:int=Form(...),target_id:int=Form(...),
    request_type:str=Form(...),weekly_hours:float=Form(...),target_allocation_id:int=Form(0),
    reason:str=Form(...),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=teacher(request,db);check_csrf(request,csrf)
    source=db.get(Allocation,source_id);target=db.get(Employee,target_id)
    if not source or source.employee_id!=u.employee_id or source.state!='approved':
        raise HTTPException(404,'O‘zingizga tegishli tasdiqlangan soatni tanlang')
    if not target or target.school_id!=u.school_id or not target.active or target.id==u.employee_id:
        raise HTTPException(400,'Qabul qiluvchi boshqa maktabda yoki mavjud emas')
    if request_type not in ('transfer','swap') or weekly_hours<=0 or weekly_hours>source.weekly_hours or round(weekly_hours*2)!=weekly_hours*2:
        raise HTTPException(400,'So‘rov turi yoki soat noto‘g‘ri')
    if len(reason.strip())<10: raise HTTPException(400,'So‘rov sababini kamida 10 belgi bilan ko‘rsating')
    if request_type=='swap':
        other=db.get(Allocation,target_allocation_id)
        if not other or other.employee_id!=target_id or other.state!='approved' or other.weekly_hours<weekly_hours:
            raise HTTPException(400,'Almashtiriladigan yuklama to‘g‘ri tanlanmagan')
    r=HourChangeRequest(school_id=u.school_id,requester_id=u.employee_id,source_allocation_id=source.id,
       target_employee_id=target_id,target_allocation_id=target_allocation_id if request_type=='swap' else None,
       request_type=request_type,weekly_hours=weekly_hours,reason=reason.strip())
    db.add(r);db.flush();audit(db,u,'request.create',u.school_id,'request',r.id)
    db.commit();return back('/me','So‘rov yuborildi')

@router.post('/requests/{rid}/consent')
def consent_request(rid:int,request:Request,choice:str=Form(...),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=teacher(request,db);check_csrf(request,csrf)
    r=db.get(HourChangeRequest,rid)
    if not r or r.target_employee_id!=u.employee_id or r.school_id!=u.school_id or r.status!='pending':
        raise HTTPException(404,'Qabul qilish uchun so‘rov topilmadi')
    if choice not in ('accept','reject'):raise HTTPException(400,'Noto‘g‘ri tanlov')
    if choice=='accept':r.recipient_consented=True
    else:r.status='rejected'
    audit(db,u,'request.consent.'+choice,u.school_id,'request',r.id)
    db.commit();return back('/me','Rozilik qayd etildi')
