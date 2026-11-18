import os
from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends,Request,HTTPException
from fastapi.responses import RedirectResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from .db import get_db
from .models import School,Employee,Allocation,HourChangeRequest,BonusAssessment,AuditLog,User,ClassGroup
from .security import current_user
from .ui import page
from .controllers import auth,district,school,teacher,bonus

app=FastAPI(title='EduTarif 3271',version='0.1.0',docs_url=None,redoc_url=None)
SECRET=os.getenv('SESSION_SECRET')
if not SECRET or len(SECRET)<32 or SECRET.startswith('CHANGE_ME'):
    raise RuntimeError('SESSION_SECRET talab etiladi: .env.example asosida xavfsiz .env yarating')
app.add_middleware(SessionMiddleware,secret_key=SECRET,https_only=os.getenv('COOKIE_SECURE','false').lower()=='true',
                   same_site='lax',max_age=60*60*8)
app.mount('/static',StaticFiles(directory='app/static'),name='static')
for router in [auth.router,district.router,school.router,teacher.router,bonus.router]:
    app.include_router(router)

@app.exception_handler(401)
def unauthorized(request:Request,exc:HTTPException):
    return RedirectResponse('/login',status_code=303)

@app.get('/health')
def health():return {'status':'ok','app':'edutarif'}

@app.get('/')
def dashboard(request:Request,db:Session=Depends(get_db)):
    u=current_user(request,db)
    if u.must_change_password:return RedirectResponse('/change-password',status_code=303)
    if u.role=='teacher':return RedirectResponse('/me',status_code=303)
    if u.role=='bonus_committee':return RedirectResponse('/bonus',status_code=303)
    if u.role=='district_admin':
        stats={'schools':db.scalar(select(func.count(School.id))) or 0,
          'teachers':db.scalar(select(func.count(Employee.id)).where(Employee.staff_type=='teacher')) or 0,
          'allocations':db.scalar(select(func.count(Allocation.id))) or 0,
          'requests':db.scalar(select(func.count(HourChangeRequest.id)).where(HourChangeRequest.status=='pending')) or 0}
    else:
        sid=u.school_id
        stats={'schools':1,
          'teachers':db.scalar(select(func.count(Employee.id)).where(Employee.school_id==sid,Employee.staff_type=='teacher')) or 0,
          'classes':db.scalar(select(func.count(ClassGroup.id)).where(ClassGroup.school_id==sid)) or 0,
          'requests':db.scalar(select(func.count(HourChangeRequest.id)).where(HourChangeRequest.school_id==sid,HourChangeRequest.status=='pending')) or 0}
    return page(request,'dashboard.html',db,stats=stats)
