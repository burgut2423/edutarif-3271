from fastapi import APIRouter,Depends,Form,Request,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..db import get_db
from ..models import District,School,User,AcademicYear,Subject,AuditLog
from ..security import check_csrf,hash_password
from ..services import audit
from ..ui import district_admin,page,back

router=APIRouter(prefix='/district')

@router.get('/schools')
def schools(request:Request,db:Session=Depends(get_db)):
    district_admin(request,db)
    schools=db.scalars(select(School).order_by(School.code)).all()
    admins=db.scalars(select(User).where(User.role=='school_admin')).all()
    return page(request,'schools.html',db,schools=schools,admins=admins)

@router.post('/schools')
def add_school(request:Request,code:str=Form(...),name:str=Form(...),address:str=Form(''),language:str=Form('uz'),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=district_admin(request,db);check_csrf(request,csrf)
    code=code.strip().upper();name=name.strip()
    if not code or not name: raise HTTPException(400,'Maktab kodi va nomi majburiy')
    if db.scalar(select(School).where(School.code==code)): raise HTTPException(409,'Maktab kodi band')
    district=db.scalar(select(District).order_by(District.id))
    s=School(district_id=district.id,code=code,name=name,address=address,language=language)
    db.add(s);db.flush();audit(db,u,'school.create',s.id,'school',s.id,name);db.commit()
    return back('/district/schools','Maktab yaratildi')

@router.post('/schools/{school_id}/admin')
def create_school_admin(school_id:int,request:Request,full_name:str=Form(...),username:str=Form(...),password:str=Form(...),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=district_admin(request,db);check_csrf(request,csrf)
    if not db.get(School,school_id): raise HTTPException(404,'Maktab topilmadi')
    if db.scalar(select(User).where(User.username==username.strip())): raise HTTPException(409,'Login mavjud')
    try: ph=hash_password(password)
    except ValueError as e:raise HTTPException(400,str(e))
    new=User(full_name=full_name.strip(),username=username.strip(),password_hash=ph,role='school_admin',school_id=school_id)
    db.add(new);db.flush();audit(db,u,'school.admin.create',school_id,'user',new.id);db.commit()
    return back('/district/schools','Maktab administratori yaratildi')

@router.post('/schools/{school_id}/toggle')
def toggle_school(school_id:int,request:Request,csrf:str=Form(...),db:Session=Depends(get_db)):
    u=district_admin(request,db);check_csrf(request,csrf)
    s=db.get(School,school_id)
    if not s: raise HTTPException(404,'Maktab topilmadi')
    s.active=not s.active;audit(db,u,'school.toggle',school_id,'school',s.id,s.active);db.commit()
    return back('/district/schools')

@router.get('/settings')
def settings(request:Request,db:Session=Depends(get_db)):
    district_admin(request,db)
    return page(request,'settings.html',db,years=db.scalars(select(AcademicYear).order_by(AcademicYear.id.desc())).all(),
                subjects=db.scalars(select(Subject).order_by(Subject.name)).all())

@router.post('/years')
def years(request:Request,name:str=Form(...),source:str=Form(''),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=district_admin(request,db);check_csrf(request,csrf)
    if db.scalar(select(AcademicYear).where(AcademicYear.name==name)):raise HTTPException(409,'O‘quv yili mavjud')
    for y in db.scalars(select(AcademicYear).where(AcademicYear.active==True)): y.active=False
    y=AcademicYear(name=name,active=True,curriculum_source=source)
    db.add(y);db.flush();audit(db,u,'year.create',None,'year',y.id);db.commit()
    return back('/district/settings')

@router.post('/subjects')
def subjects(request:Request,code:str=Form(...),name:str=Form(...),grades_from:int=Form(1),grades_to:int=Form(11),csrf:str=Form(...),db:Session=Depends(get_db)):
    u=district_admin(request,db);check_csrf(request,csrf)
    if not 1<=grades_from<=grades_to<=11:raise HTTPException(400,'Sinf chegarasi noto‘g‘ri')
    if db.scalar(select(Subject).where(Subject.code==code.strip())):raise HTTPException(409,'Fan kodi mavjud')
    item=Subject(code=code.strip(),name=name.strip(),grades_from=grades_from,grades_to=grades_to)
    db.add(item);db.flush();audit(db,u,'subject.create',None,'subject',item.id);db.commit()
    return back('/district/settings')

@router.get('/audit')
def audit_logs(request:Request,db:Session=Depends(get_db)):
    district_admin(request,db)
    return page(request,'audit.html',db,logs=db.scalars(select(AuditLog).order_by(AuditLog.at.desc()).limit(200)).all())
