from datetime import date
from fastapi import APIRouter,Depends,Form,Request,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import get_db
from ..models import (School,User,Employee,EmployeeSubject,Subject,ClassGroup,AcademicYear,
                      CurriculumLine,Allocation,CouncilDecision,HourChangeRequest)
from ..security import check_csrf,hash_password
from ..services import (PRIORITY_LABELS,distribution_preview,used_rate,validate_allocation,
                        qualified,priority_rank,hours_total,audit)
from ..ui import admin,page,back

router=APIRouter(prefix='/school')

def active_year(db):
    year=db.scalar(select(AcademicYear).where(AcademicYear.active==True))
    if not year:raise HTTPException(409,'Tuman administratori faol o‘quv yilini yaratishi kerak')
    return year

def scoped_class(db,school_id,class_id):
    c=db.get(ClassGroup,class_id)
    if not c or c.school_id!=school_id:raise HTTPException(404,'Sinf topilmadi')
    return c

def scoped_employee(db,school_id,employee_id):
    e=db.get(Employee,employee_id)
    if not e or e.school_id!=school_id:raise HTTPException(404,'Xodim topilmadi')
    return e

def scoped_line(db,school_id,line_id):
    line=db.get(CurriculumLine,line_id)
    if not line or line.klass.school_id!=school_id:raise HTTPException(404,'Setka satri topilmadi')
    return line

def scoped_allocation(db,school_id,allocation_id):
    a=db.get(Allocation,allocation_id)
    if not a or a.line.klass.school_id!=school_id:raise HTTPException(404,'Yuklama topilmadi')
    return a

@router.get('/staff')
def staff(request:Request,db:Session=Depends(get_db)):
    u=admin(request,db)
    employees=db.scalars(select(Employee).where(Employee.school_id==u.school_id).order_by(Employee.full_name)).all()
    subjects=db.scalars(select(Subject).order_by(Subject.name)).all()
    es=db.scalars(select(EmployeeSubject).join(Employee).where(Employee.school_id==u.school_id)).all()
    return page(request,'staff.html',db,employees=employees,subjects=subjects,es=es,priority_labels=PRIORITY_LABELS)

@router.post('/staff')
def add_employee(request:Request,full_name:str=Form(...),username:str=Form(''),password:str=Form(''),
    staff_type:str=Form('teacher'),degree:str=Form('higher'),employment_type:str=Form('main'),
    qualification:str=Form('none'),priority_basis:str=Form('higher_none'),
    national_certificate:bool=Form(False),retraining_diploma:bool=Form(False),
    primary_specialist:bool=Form(False),base_salary:float=Form(0),
    qualification_valid_until:str=Form(''),certificate_valid_until:str=Form(''),
    priority_evidence:str=Form(''),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf)
    if staff_type not in ('teacher','psychologist','librarian','director','deputy','other'):
        raise HTTPException(400,'Lavozim turi noto‘g‘ri')
    if priority_basis not in PRIORITY_LABELS:raise HTTPException(400,'Ustuvorlik turi noto‘g‘ri')
    if base_salary<0:raise HTTPException(400,'Tarif stavkasi manfiy emas')
    if username and db.scalar(select(User).where(User.username==username.strip())):raise HTTPException(409,'Login mavjud')
    if username:
        try: ph=hash_password(password)
        except ValueError as ex:raise HTTPException(400,str(ex))
    def parse(s):
        try:return date.fromisoformat(s) if s else None
        except ValueError:raise HTTPException(400,'Sana YYYY-MM-DD bo‘lishi shart')
    e=Employee(school_id=u.school_id,full_name=full_name.strip(),staff_type=staff_type,
        degree=degree,employment_type=employment_type,qualification=qualification,
        priority_basis=priority_basis,national_certificate=national_certificate,
        retraining_diploma=retraining_diploma,primary_specialist=primary_specialist,
        base_salary=base_salary,priority_evidence=priority_evidence,
        qualification_valid_until=parse(qualification_valid_until),certificate_valid_until=parse(certificate_valid_until))
    db.add(e);db.flush()
    if username:
        account=User(school_id=u.school_id,employee_id=e.id,full_name=e.full_name,
                     username=username.strip(),password_hash=ph,role='teacher')
        db.add(account)
    audit(db,u,'employee.create',u.school_id,'employee',e.id);db.commit()
    return back('/school/staff','Xodim qo‘shildi')

@router.post('/staff/{employee_id}/update')
def update_employee(employee_id:int,request:Request,qualification:str=Form(...),
    priority_basis:str=Form(...),priority_evidence:str=Form(''),base_salary:float=Form(0),
    primary_specialist:bool=Form(False),active:bool=Form(False),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf)
    e=scoped_employee(db,u.school_id,employee_id)
    if qualification not in ('top','first','second','none') or priority_basis not in PRIORITY_LABELS or base_salary<0:
        raise HTTPException(400,'Malaka / stavka maʼlumotlari noto‘g‘ri')
    e.qualification=qualification;e.priority_basis=priority_basis
    e.priority_evidence=priority_evidence;e.base_salary=base_salary
    e.primary_specialist=primary_specialist;e.active=active
    if not active:
        account=db.scalar(select(User).where(User.employee_id==e.id))
        if account:account.active=False
    audit(db,u,'employee.update',u.school_id,'employee',e.id)
    db.commit();return back('/school/staff','Xodim maʼlumoti yangilandi')

@router.post('/staff/{employee_id}/subject')
def employee_subject(employee_id:int,request:Request,subject_id:int=Form(...),primary_methodology:bool=Form(False),
    qualification_note:str=Form(''),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf);scoped_employee(db,u.school_id,employee_id)
    sub=db.get(Subject,subject_id)
    if not sub:raise HTTPException(404,'Fan topilmadi')
    if db.scalar(select(EmployeeSubject).where(EmployeeSubject.employee_id==employee_id,EmployeeSubject.subject_id==subject_id)):
        raise HTTPException(409,'Fan biriktirilgan')
    db.add(EmployeeSubject(employee_id=employee_id,subject_id=subject_id,
                           primary_methodology=primary_methodology,qualification_note=qualification_note))
    audit(db,u,'employee.subject.add',u.school_id,'employee',employee_id,f'fan={subject_id}')
    db.commit();return back('/school/staff','Xodimga fan biriktirildi')

@router.get('/classes')
def classes(request:Request,db:Session=Depends(get_db)):
    u=admin(request,db);y=active_year(db)
    items=db.scalars(select(ClassGroup).where(ClassGroup.school_id==u.school_id,ClassGroup.year_id==y.id)
                     .order_by(ClassGroup.grade,ClassGroup.section)).all()
    return page(request,'classes.html',db,classes=items)

@router.post('/classes')
def add_class(request:Request,grade:int=Form(...),section:str=Form(...),
  student_count:int=Form(...),language:str=Form('uz'),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf);y=active_year(db)
    if not 1<=grade<=11 or not 1<=student_count<=60 or len(section.strip())>8:
        raise HTTPException(400,'Sinf yoki o‘quvchilar soni noto‘g‘ri')
    normalized_section=section.strip().upper()
    if not normalized_section:raise HTTPException(400,'Sinf harfini kiriting')
    existing=db.scalar(select(ClassGroup).where(ClassGroup.school_id==u.school_id,
       ClassGroup.year_id==y.id,ClassGroup.grade==grade,ClassGroup.section==normalized_section,ClassGroup.language==language))
    if existing:raise HTTPException(409,'Sinf mavjud')
    c=ClassGroup(school_id=u.school_id,year_id=y.id,grade=grade,section=normalized_section,
                 student_count=student_count,language=language)
    db.add(c);db.flush();audit(db,u,'class.create',u.school_id,'class',c.id)
    db.commit();return back('/school/classes','Sinf qo‘shildi')

@router.post('/classes/{class_id}/approve')
def approve_class(class_id:int,request:Request,csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf);c=scoped_class(db,u.school_id,class_id)
    c.approved=True;audit(db,u,'class.verify',u.school_id,'class',c.id)
    db.commit();return back('/school/classes')

@router.get('/grid')
def grid(request:Request,db:Session=Depends(get_db)):
    u=admin(request,db);y=active_year(db)
    classes=db.scalars(select(ClassGroup).where(ClassGroup.school_id==u.school_id,ClassGroup.year_id==y.id)
                       .order_by(ClassGroup.grade,ClassGroup.section)).all()
    lines=db.scalars(select(CurriculumLine).join(ClassGroup).where(ClassGroup.school_id==u.school_id,
                           ClassGroup.year_id==y.id).order_by(ClassGroup.grade,ClassGroup.section)).all()
    subjects=db.scalars(select(Subject).order_by(Subject.name)).all()
    return page(request,'grid.html',db,classes=classes,lines=lines,subjects=subjects,
                allocated={line.id:hours_total(db,line.id) for line in lines})

@router.post('/grid')
def add_grid(request:Request,class_id:int=Form(...),subject_id:int=Form(...),
  weekly_hours:float=Form(...),groups:int=Form(1),source_ref:str=Form(''),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf)
    c=scoped_class(db,u.school_id,class_id);s=db.get(Subject,subject_id)
    if not s or not s.grades_from<=c.grade<=s.grades_to:raise HTTPException(400,'Fan sinfga mos emas')
    if not 0<weekly_hours<=15 or groups not in (1,2,3,4) or round(weekly_hours*2)!=weekly_hours*2:
        raise HTTPException(400,'Soat yoki guruh qiymati noto‘g‘ri')
    if db.scalar(select(CurriculumLine).where(CurriculumLine.class_id==class_id,CurriculumLine.subject_id==subject_id)):
        raise HTTPException(409,'Bu fan setkada mavjud')
    line=CurriculumLine(class_id=class_id,subject_id=subject_id,weekly_hours=weekly_hours,
                        groups=groups,source_ref=source_ref)
    db.add(line);db.flush();audit(db,u,'grid.add',u.school_id,'line',line.id)
    db.commit();return back('/school/grid','Fan setkaga qo‘shildi')

@router.post('/grid/{line_id}/verify')
def verify_grid(line_id:int,request:Request,csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf);line=scoped_line(db,u.school_id,line_id)
    if not line.klass.approved or not line.source_ref.strip():
        raise HTTPException(400,'Sinf tasdiqlangan va setka manbasi kiritilgan bo‘lishi shart')
    line.verified=True;audit(db,u,'grid.verify',u.school_id,'line',line.id)
    db.commit();return back('/school/grid')

@router.get('/allocations')
def allocations(request:Request,db:Session=Depends(get_db)):
    u=admin(request,db);y=active_year(db)
    lines=db.scalars(select(CurriculumLine).join(ClassGroup).where(ClassGroup.school_id==u.school_id,
              ClassGroup.year_id==y.id).order_by(ClassGroup.grade,ClassGroup.section)).all()
    people=db.scalars(select(Employee).where(Employee.school_id==u.school_id,Employee.active==True,
                                Employee.staff_type=='teacher').order_by(Employee.full_name)).all()
    asn=db.scalars(select(Allocation).join(CurriculumLine).join(ClassGroup).where(ClassGroup.school_id==u.school_id,
                      ClassGroup.year_id==y.id).order_by(Allocation.id.desc())).all()
    decisions=db.scalars(select(CouncilDecision).where(CouncilDecision.school_id==u.school_id,
                      CouncilDecision.year_id==y.id,CouncilDecision.kind=='hours').order_by(CouncilDecision.id.desc())).all()
    totals={line.id:hours_total(db,line.id) for line in lines}
    workloads={p.id:used_rate(db,p.id,year_id=y.id) for p in people}
    return page(request,'allocations.html',db,lines=lines,people=people,allocations=asn,
                decisions=decisions,totals=totals,workloads=workloads)

@router.get('/allocations/export.csv')
def export_allocations(request:Request,db:Session=Depends(get_db)):
    """Excel-compatible district-safe *single school* CSV for active academic year."""
    import csv
    import io
    from fastapi.responses import Response
    u=admin(request,db); y=active_year(db)
    records=db.scalars(select(Allocation).join(CurriculumLine).join(ClassGroup).where(
        ClassGroup.school_id==u.school_id,ClassGroup.year_id==y.id)
        .order_by(ClassGroup.grade,ClassGroup.section,Allocation.id)).all()
    stream=io.StringIO()
    writer=csv.writer(stream)
    writer.writerow(['O‘quv yili','Sinf','Fan','O‘qituvchi','Haftalik soat','Holat','Kengash bayonnomasi'])
    def safe(value):
        s=str(value or '')
        return "'"+s if s.lstrip().startswith(('=','+','-','@')) else s
    for a in records:
        writer.writerow([safe(y.name),safe(f'{a.line.klass.grade}-{a.line.klass.section}'),
            safe(a.line.subject.name),safe(a.employee.full_name),a.weekly_hours,
            safe(a.state),safe(a.decision.number if a.decision else '')])
    payload=('\ufeff'+stream.getvalue()).encode('utf-8')
    return Response(payload,media_type='text/csv; charset=utf-8',headers={
        'Content-Disposition':f'attachment; filename="edutarif-school-{u.school_id}-year-{y.id}.csv"',
        'Cache-Control':'no-store'})

@router.post('/allocations')
def add_allocation(request:Request,line_id:int=Form(...),employee_id:int=Form(...),weekly_hours:float=Form(...),
 csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf)
    line=scoped_line(db,u.school_id,line_id);emp=scoped_employee(db,u.school_id,employee_id)
    try:validate_allocation(db,line,emp,weekly_hours)
    except ValueError as exc:raise HTTPException(400,str(exc))
    a=Allocation(line_id=line.id,employee_id=emp.id,weekly_hours=weekly_hours,created_by=u.id)
    db.add(a);db.flush();audit(db,u,'allocation.create',u.school_id,'allocation',a.id)
    db.commit();return back('/school/allocations','Dars yuklamasi loyihasi yaratildi')

@router.get('/allocations/preview/{line_id}')
def preview(line_id:int,request:Request,db:Session=Depends(get_db)):
    u=admin(request,db);line=scoped_line(db,u.school_id,line_id)
    return page(request,'preview.html',db,line=line,proposals=distribution_preview(db,line),
                used=hours_total(db,line.id))

@router.post('/allocations/autofill/{line_id}')
def autofill(line_id:int,request:Request,csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf)
    line=scoped_line(db,u.school_id,line_id)
    if not line.verified or not line.klass.approved:raise HTTPException(400,'Setka tasdiqlanmagan')
    proposals=distribution_preview(db,line)
    if not proposals:raise HTTPException(400,'Mos o‘qituvchi yoki bo‘sh soat topilmadi')
    for p in proposals:
        try:validate_allocation(db,line,p['employee'],p['hours'])
        except ValueError as exc:raise HTTPException(400,str(exc))
        db.add(Allocation(line_id=line.id,employee_id=p['employee'].id,
               weekly_hours=p['hours'],created_by=u.id))
        db.flush()
    audit(db,u,'allocation.autofill.draft',u.school_id,'line',line.id,f'{len(proposals)} ta tavsiya')
    db.commit();return back('/school/allocations','Avtomatik takliflar loyiha sifatida yaratildi')

@router.post('/council')
def create_council(request:Request,number:str=Form(...),council_date:str=Form(...),
   document_ref:str=Form(...),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf);y=active_year(db)
    if not document_ref.strip():raise HTTPException(400,'Bayonnoma havolasi yoki raqami kerak')
    try:d=date.fromisoformat(council_date)
    except ValueError:raise HTTPException(400,'Bayonnoma sanasi noto‘g‘ri')
    c=CouncilDecision(school_id=u.school_id,year_id=y.id,number=number,date=d,kind='hours',
                      document_ref=document_ref,approved=True,created_by=u.id)
    db.add(c);db.flush();audit(db,u,'council.record',u.school_id,'council',c.id)
    db.commit();return back('/school/allocations','Bayonnoma qayd etildi')

@router.post('/allocations/{allocation_id}/approve')
def approve_allocation(allocation_id:int,request:Request,decision_id:int=Form(...),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf);a=scoped_allocation(db,u.school_id,allocation_id)
    decision=db.get(CouncilDecision,decision_id)
    if not decision or decision.school_id!=u.school_id or not decision.approved or decision.kind!='hours' or decision.year_id != a.line.klass.year_id:
        raise HTTPException(400,'Shu o‘quv yiliga oid tasdiqlangan pedagogik kengash bayonnomasi talab etiladi')
    try:validate_allocation(db,a.line,a.employee,a.weekly_hours,exclude_allocation=a.id)
    except ValueError as exc:raise HTTPException(400,str(exc))
    a.state='approved';a.decision_id=decision.id
    audit(db,u,'allocation.approve',u.school_id,'allocation',a.id,f'council={decision.id}')
    db.commit();return back('/school/allocations','Yuklama tasdiqlandi')

@router.get('/requests')
def requests(request:Request,db:Session=Depends(get_db)):
    u=admin(request,db)
    items=db.scalars(select(HourChangeRequest).where(HourChangeRequest.school_id==u.school_id)
                     .order_by(HourChangeRequest.created_at.desc())).all()
    people={x.id:x.full_name for x in db.scalars(select(Employee).where(Employee.school_id==u.school_id))}
    return page(request,'requests.html',db,requests=items,people=people)

@router.post('/requests/{rid}/decide')
def decide_request(rid:int,request:Request,action:str=Form(...),decision_id:int=Form(0),
                      manager_note:str=Form(''),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=admin(request,db);check_csrf(request,csrf)
    r=db.get(HourChangeRequest,rid)
    if not r or r.school_id!=u.school_id:raise HTTPException(404,'So‘rov topilmadi')
    if r.status!='pending':raise HTTPException(409,'So‘rov allaqachon ko‘rib chiqilgan')
    if action not in ('approve','reject'):raise HTTPException(400,'Amal noto‘g‘ri')
    if action=='approve':
        if not r.recipient_consented:raise HTTPException(400,'Qabul qiluvchi o‘qituvchi roziligi talab etiladi')
        decision=db.get(CouncilDecision,decision_id)
        if not decision or decision.school_id!=u.school_id or not decision.approved or decision.kind!='hours' or decision.year_id!=scoped_allocation(db,u.school_id,r.source_allocation_id).line.klass.year_id:
            raise HTTPException(400,'Pedagogik kengashning tasdiqlangan bayonnomasi kerak')
        source=scoped_allocation(db,u.school_id,r.source_allocation_id)
        target=scoped_employee(db,u.school_id,r.target_employee_id)
        if source.employee_id!=r.requester_id or source.state!='approved' or source.weekly_hours<r.weekly_hours:
            raise HTTPException(400,'Asl yuklama yoki so‘rov muallifi mos emas')
        if not qualified(db,target,source.line):raise HTTPException(400,'Qabul qiluvchi fan bo‘yicha malakaga ega emas')
        if r.request_type=='transfer':
            # Fan umumiy soati o'zgarmaydi: beruvchi ulushi qabul qiluvchiga o'tadi.
            from ..services import MAX_RATE,used_rate
            rate=used_rate(db,target.id,year_id=source.line.klass.year_id)+r.weekly_hours/(18 if source.line.klass.grade<=4 else 20)
            if rate>MAX_RATE+0.001:raise HTTPException(400,'Qabul qiluvchi 1.5 stavkadan oshadi')
            source.weekly_hours=round(source.weekly_hours-r.weekly_hours,2)
            if source.weekly_hours<0.001:source.state='superseded'  # retain FK/audit history
            db.add(Allocation(line_id=source.line_id,employee_id=target.id,weekly_hours=r.weekly_hours,
                              state='approved',decision_id=decision.id,created_by=u.id))
        elif r.request_type=='swap':
            other=scoped_allocation(db,u.school_id,r.target_allocation_id or 0)
            if other.employee_id!=target.id or other.state!='approved' or other.weekly_hours<r.weekly_hours:
                raise HTTPException(400,'Qarshi o‘qituvchi yuklamasi yetarli emas')
            if not qualified(db,source.employee,other.line):raise HTTPException(400,'O‘zaro fan malakasi yetarli emas')
            from ..services import MAX_RATE,used_rate
            source_final=used_rate(db,source.employee_id,year_id=source.line.klass.year_id)-r.weekly_hours/(18 if source.line.klass.grade<=4 else 20)+r.weekly_hours/(18 if other.line.klass.grade<=4 else 20)
            other_final=used_rate(db,target.id,year_id=source.line.klass.year_id)-r.weekly_hours/(18 if other.line.klass.grade<=4 else 20)+r.weekly_hours/(18 if source.line.klass.grade<=4 else 20)
            if max(source_final,other_final)>MAX_RATE+0.001:raise HTTPException(400,'Almashtirishdan keyin 1.5 stavka oshadi')
            source.weekly_hours=round(source.weekly_hours-r.weekly_hours,2)
            other.weekly_hours=round(other.weekly_hours-r.weekly_hours,2)
            if source.weekly_hours<0.001:source.state='superseded'  # retain FK/audit history
            if other.weekly_hours<0.001:other.state='superseded'  # retain FK/audit history
            db.add_all([
                Allocation(line_id=source.line_id,employee_id=target.id,weekly_hours=r.weekly_hours,
                    state='approved',decision_id=decision.id,created_by=u.id),
                Allocation(line_id=other.line_id,employee_id=r.requester_id,weekly_hours=r.weekly_hours,
                    state='approved',decision_id=decision.id,created_by=u.id)])
        else:raise HTTPException(400,'So‘rov turi noto‘g‘ri')
        r.status='approved';r.council_decision_id=decision.id
    else:r.status='rejected'
    from datetime import datetime
    r.reviewed_by=u.id;r.manager_note=manager_note;r.decided_at=datetime.utcnow()
    audit(db,u,'request.'+r.status,u.school_id,'request',r.id)
    db.commit();return back('/school/requests','So‘rov ko‘rib chiqildi')
