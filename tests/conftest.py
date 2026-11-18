import os
os.environ.setdefault('SESSION_SECRET','pytest-local-session-secret-is-not-for-prod-123456789')
import re
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.db import Base,get_db
from app.main import app
from app.models import District,School,User,AcademicYear,Subject,Employee,EmployeeSubject
from app.security import hash_password

@pytest.fixture()
def db():
    eng=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    Base.metadata.create_all(eng)
    with sessionmaker(bind=eng,expire_on_commit=False)() as s:
        s.add(District(name='Test tuman'))
        s.add(AcademicYear(name='2026/2027',active=True))
        s.add(Subject(code='MAT',name='Matematika',grades_from=1,grades_to=11))
        s.add(User(username='district',password_hash=hash_password('district-test-password'),
                   full_name='Tuman',role='district_admin',must_change_password=False))
        s.commit()
        yield s
    eng.dispose()

@pytest.fixture()
def client(db):
    def override():yield db
    app.dependency_overrides[get_db]=override
    with TestClient(app,follow_redirects=True) as c:
        yield c
    app.dependency_overrides.clear()

def get_csrf(resp):
    m=re.search(r'name="csrf"\s+(?:type="hidden"\s+)?value="([^"]+)"',resp.text)
    if not m:
        m=re.search(r'type="hidden"\s+name="csrf"\s+value="([^"]+)"',resp.text)
    assert m,f'no csrf in page: {resp.text[:400]}'
    return m.group(1)

def login(client,username,password):
    token=get_csrf(client.get('/login'))
    r=client.post('/login',data={'csrf':token,'username':username,'password':password})
    assert r.status_code==200,(r.status_code,r.text[:300])
    return r

def csrf_on(client,path='/'):
    return get_csrf(client.get(path))
