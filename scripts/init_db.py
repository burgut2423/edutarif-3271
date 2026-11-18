"""Database tables and generic subject catalog. No official curriculum hours are seeded."""
from sqlalchemy import select
from app.db import Base, engine, SessionLocal
from app.models import District, AcademicYear, Subject, PolicyVersion
from datetime import date

SUBJECTS = [
    ('ONA_TILI','Ona tili',1,11),('OQISH','O‘qish savodxonligi',1,4),
    ('MAT','Matematika',1,11),('ING','Ingliz tili',1,11),
    ('RUS','Rus tili',1,11),('TARIX','Tarix',5,11),
    ('FIZ','Fizika',6,11),('KIM','Kimyo',7,11),('BIO','Biologiya',5,11),
    ('GEOG','Geografiya',5,11),('INF','Informatika',5,11),
    ('JIS','Jismoniy tarbiya',1,11),('MUS','Musiqa madaniyati',1,7),
    ('TEX','Texnologiya',1,9),('TAS','Tasviriy sanʼat',1,7),
    ('TAB','Tabiiy fanlar',1,6),('ADAB','Adabiyot',5,11),
    ('TARBIYA','Tarbiya',1,11),('ALG','Algebra',7,11),('GEO','Geometriya',7,11),
]

def init():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.scalar(select(District).limit(1)):
            db.add(District(name="Qo‘shko‘pir tumani"))
        if not db.scalar(select(AcademicYear).where(AcademicYear.name=='2026/2027')):
            db.add(AcademicYear(name='2026/2027',active=True,start_date=date(2026,9,1),
              end_date=date(2027,5,31),curriculum_source='MMTV 2026-04-10 133-son buyruq (hujjatni tekshiring)'))
        for code,name,lo,hi in SUBJECTS:
            if not db.scalar(select(Subject).where(Subject.code==code)):
                db.add(Subject(code=code,name=name,grades_from=lo,grades_to=hi))
        if not db.scalar(select(PolicyVersion).where(PolicyVersion.code=='3271-1-2026')):
            db.add(PolicyVersion(code='3271-1-2026',valid_from=date(2026,8,1),
              source_url='https://lex.uz/acts/-4919258',params={'primary_rate':18,'secondary_rate':20,'max_rate':1.5,
              'annual_max_hours':2322,'priority_version':'2026-08-01'},locked=True))
        if not db.scalar(select(PolicyVersion).where(PolicyVersion.code=='823-617-2026')):
            db.add(PolicyVersion(code='823-617-2026',valid_from=date(2026,11,12),
              source_url='https://lex.uz/docs/-4532496',params={'pedagogue_recipient_fraction':0.5,
              'committee_min_size':7,'committee_quorum_fraction':0.6666667},locked=True))
        db.commit()
    print('Bazaviy jadvallar tayyor. Fanlar — boshlang‘ich katalog; rasmiy soatlar yuklanmagan.')

if __name__=='__main__':init()
