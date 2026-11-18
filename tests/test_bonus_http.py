from sqlalchemy import select
from app.models import School,User,Employee,BonusPeriod,BonusAssessment,BonusMeeting
from app.security import hash_password
from .conftest import login,csrf_on


def test_bonus_workflow_needs_meeting_and_quorum(client,db):
    school=School(district_id=1,code='BONUS',name='Test Bonus School')
    db.add(school);db.flush()
    db.add(User(school_id=school.id,username='manager',full_name='Manager',role='school_admin',
                password_hash=hash_password('manager-password-long'),must_change_password=False))
    db.add(User(school_id=school.id,username='committee',full_name='Committee',role='bonus_committee',
                password_hash=hash_password('committee-password-long'),must_change_password=False))
    e1=Employee(school_id=school.id,full_name='Pedagog A',staff_type='teacher',base_salary=3_000_000)
    e2=Employee(school_id=school.id,full_name='Pedagog B',staff_type='teacher',base_salary=3_000_000)
    db.add_all([e1,e2]);db.commit()
    login(client,'manager','manager-password-long')
    csrf=csrf_on(client,'/bonus')
    r=client.post('/bonus/periods',data={'csrf':csrf,'name':'2026/2027','fund_limit':'5000000',
           'group_member_count':7,'group_protocol':'1-son bayonnoma'})
    assert r.status_code==200
    p=db.scalar(select(BonusPeriod).where(BonusPeriod.school_id==school.id))
    r=client.post('/bonus/assessments',data={'csrf':csrf,'period_id':p.id,'employee_id':e1.id,
               'score':95,'evidence':'2026 baholash varaqasi'})
    assert r.status_code==200
    a=db.scalar(select(BonusAssessment).where(BonusAssessment.period_id==p.id))
    assert a.rate==35
    client.post('/logout',data={'csrf':csrf})
    login(client,'committee','committee-password-long')
    csrf=csrf_on(client,'/bonus')
    r=client.post(f'/bonus/assessments/{a.id}/approve',data={'csrf':csrf,'meeting_id':12345})
    assert r.status_code==400 # No meeting => no single-user approval
    # 4 of 7 is less than 2/3 quorum
    data={'csrf':csrf,'period_id':p.id,'held_on':'2026-06-30','protocol_ref':'meeting-1',
         'director_order_ref':'order-1','attendees':4,'votes_for':4,'votes_against':0,
         'labor_union_present':'true','parent_present':'true','supervisory_board_present':'true'}
    r=client.post('/bonus/meetings',data=data)
    assert r.status_code==400
    data.update({'attendees':5,'votes_for':2,'votes_against':1,'votes_abstain':2})
    # Abstentions cannot manufacture a majority.
    assert client.post('/bonus/meetings',data=data).status_code==400
    data['attendees']=5;data['votes_for']=5;data['votes_against']=0;data['votes_abstain']=0
    r=client.post('/bonus/meetings',data=data)
    assert r.status_code==200
    m=db.scalar(select(BonusMeeting).where(BonusMeeting.period_id==p.id))
    r=client.post(f'/bonus/assessments/{a.id}/approve',data={'csrf':csrf,'meeting_id':m.id})
    assert r.status_code==200
    assert a.state=='approved'
    assert a.amount==1_050_000
