from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from .security import current_user, csrf_token, require_role
from .models import AcademicYear

templates=Jinja2Templates(directory='app/templates')

def page(request:Request, template:str, db:Session, **kwargs):
    user=current_user(request,db)
    ctx={'user':user,'csrf':csrf_token(request),'active_year':db.query(AcademicYear).filter_by(active=True).first()}
    ctx.update(kwargs)
    return templates.TemplateResponse(request,template,ctx)

def admin(request,db):
    u=current_user(request,db)
    if u.must_change_password: raise HTTPException(403,'Avval parolingizni o‘zgartiring')
    require_role(u,'school_admin')
    return u

def district_admin(request,db):
    u=current_user(request,db)
    if u.must_change_password: raise HTTPException(403,'Avval parolingizni o‘zgartiring')
    require_role(u,'district_admin')
    return u

def teacher(request,db):
    u=current_user(request,db)
    if u.must_change_password: raise HTTPException(403,'Avval parolingizni o‘zgartiring')
    require_role(u,'teacher')
    return u

def back(path, msg=None):
    return RedirectResponse(path+(('?msg='+__import__('urllib.parse',fromlist=['quote']).quote(msg)) if msg else ''),status_code=303)
