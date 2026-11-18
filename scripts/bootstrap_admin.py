import os
from sqlalchemy import select
from dotenv import load_dotenv
load_dotenv()
from app.db import SessionLocal
from app.models import District, User
from app.security import hash_password
from scripts.db_migrate import migrate_to_head

if __name__=='__main__':
    migrate_to_head()
    name=os.getenv('BOOTSTRAP_NAME','Tuman administratori')
    username=os.getenv('BOOTSTRAP_USERNAME','tumanadmin')
    password=os.getenv('BOOTSTRAP_PASSWORD','')
    if not password or password.startswith('CHANGE_ME'):
        raise SystemExit('BOOTSTRAP_PASSWORD ni .env faylida 12+ belgili maxfiy parolga almashtiring')
    with SessionLocal() as db:
        if not db.scalar(select(District).limit(1)):
            db.add(District(name=os.getenv("DISTRICT_NAME", "Qo‘shko‘pir tumani")))
            db.flush()
        if db.scalar(select(User).where(User.username==username)):
            raise SystemExit('Administrator mavjud: yangi parol bilan qayta yaratilmaydi')
        db.add(User(username=username,password_hash=hash_password(password),
                    full_name=name,role='district_admin',must_change_password=True))
        db.commit()
    print('Administrator yaratildi. Birinchi kirishda parolni o‘zgartiring.')
