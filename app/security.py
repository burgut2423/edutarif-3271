import hashlib
import hmac
import os
import secrets
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from .models import User

ITERATIONS = 420_000

def hash_password(raw: str) -> str:
    if len(raw) < 12:
        raise ValueError('Parol kamida 12 belgidan iborat bo‘lishi kerak')
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', raw.encode('utf-8'), salt, ITERATIONS)
    return f'pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}'

def verify_password(raw: str, stored: str) -> bool:
    try:
        algo, iterations, salt, key = stored.split('$')
        if algo != 'pbkdf2_sha256': return False
        comp = hashlib.pbkdf2_hmac('sha256',raw.encode('utf-8'),bytes.fromhex(salt),int(iterations))
        return hmac.compare_digest(comp, bytes.fromhex(key))
    except (TypeError, ValueError, AttributeError):
        return False

def csrf_token(request: Request) -> str:
    if 'csrf' not in request.session:
        request.session['csrf'] = secrets.token_urlsafe(32)
    return request.session['csrf']

def check_csrf(request: Request, token: str | None):
    expected = request.session.get('csrf', '')
    if not token or not expected or not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=403, detail='CSRF tekshiruvi muvaffaqiyatsiz')

def current_user(request: Request, db: Session) -> User:
    uid = request.session.get('uid')
    if not uid:
        raise HTTPException(status_code=401, detail='Tizimga kiring')
    user = db.get(User, uid)
    if not user or not user.active or (user.school_id and (not user.school or not user.school.active)):
        request.session.clear()
        raise HTTPException(status_code=401, detail='Sessiya yakunlandi')
    return user

def require_role(user: User, *roles: str):
    if user.role not in roles:
        raise HTTPException(status_code=403, detail='Ushbu amalga ruxsat yo‘q')

def school_scope(user: User, school_id: int):
    # For personal data, only own-school accounts. District admins access aggregate/school settings only.
    if user.role != 'district_admin' and user.school_id != school_id:
        raise HTTPException(status_code=403, detail='Boshqa maktab maʼlumotiga ruxsat yo‘q')

def require_employee(user: User) -> int:
    if user.role != 'teacher' or not user.employee_id:
        raise HTTPException(status_code=403, detail='O‘qituvchi profili talab etiladi')
    return user.employee_id
