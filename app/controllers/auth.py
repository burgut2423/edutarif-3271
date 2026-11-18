from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from ..db import get_db
from ..models import User
from ..security import verify_password,hash_password,csrf_token,check_csrf,current_user
from ..ui import templates,page,back

router=APIRouter()

@router.get('/login')
def login_form(request:Request):
    if request.session.get('uid'): return RedirectResponse('/',status_code=302)
    return templates.TemplateResponse(request,'login.html',{'csrf':csrf_token(request),'error':None})

@router.post('/login')
def login(request:Request,username:str=Form(...), password:str=Form(...),csrf:str=Form(...),db:Session=Depends(get_db)):
    check_csrf(request,csrf)
    user=db.scalar(select(User).where(User.username==username.strip()))
    if not user or not user.active or not verify_password(password,user.password_hash):
        return templates.TemplateResponse(request,'login.html',{'csrf':csrf_token(request),'error':'Login yoki parol noto‘g‘ri'},status_code=401)
    request.session.clear()
    request.session['uid']=user.id
    csrf_token(request)
    user.last_login=datetime.utcnow();db.commit()
    return back('/change-password' if user.must_change_password else '/')

@router.post('/logout')
def logout(request:Request,csrf:str=Form(...)):
    check_csrf(request,csrf)
    request.session.clear()
    return back('/login')

@router.get('/change-password')
def change_password_form(request:Request,db:Session=Depends(get_db)):
    return page(request,'password.html',db)

@router.post('/change-password')
def change_password(request:Request,old:str=Form(...),new:str=Form(...),csrf:str=Form(...),db:Session=Depends(get_db)):
    check_csrf(request,csrf);user=current_user(request,db)
    if not verify_password(old,user.password_hash):
        raise HTTPException(status_code=400,detail='Eski parol noto‘g‘ri')
    try: user.password_hash=hash_password(new)
    except ValueError as exc: raise HTTPException(status_code=400,detail=str(exc))
    user.must_change_password=False;db.commit()
    return back('/','Parol almashtirildi')
