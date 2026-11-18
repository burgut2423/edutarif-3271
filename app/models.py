from datetime import datetime, date
from sqlalchemy import (Boolean, Column, Date, DateTime, ForeignKey, Integer,
                        Numeric, String, Text, UniqueConstraint, Float, JSON)
from sqlalchemy.orm import relationship
from .db import Base


def now():
    return datetime.utcnow()

class District(Base):
    __tablename__ = 'districts'
    id = Column(Integer, primary_key=True)
    name = Column(String(180), nullable=False, unique=True)

class School(Base):
    __tablename__ = 'schools'
    id = Column(Integer, primary_key=True)
    district_id = Column(Integer, ForeignKey('districts.id'), nullable=False, index=True)
    code = Column(String(30), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    address = Column(String(300), default='')
    language = Column(String(30), default='uz')
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=now)
    district = relationship('District')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(260), nullable=False)
    full_name = Column(String(180), nullable=False)
    role = Column(String(30), nullable=False)  # district_admin, school_admin, teacher, bonus_committee
    school_id = Column(Integer, ForeignKey('schools.id'), index=True, nullable=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True, unique=True)
    active = Column(Boolean, nullable=False, default=True)
    must_change_password = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    school = relationship('School')
    employee = relationship('Employee', foreign_keys=[employee_id])

class AcademicYear(Base):
    __tablename__ = 'academic_years'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    active = Column(Boolean, default=False)
    curriculum_source = Column(String(300), default='')

class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    code = Column(String(40), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    grades_from = Column(Integer, default=1)
    grades_to = Column(Integer, default=11)

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False, index=True)
    full_name = Column(String(180), nullable=False)
    job_title = Column(String(130), default='O‘qituvchi')
    staff_type = Column(String(25), default='teacher')  # teacher, psychologist, librarian, director, deputy, other
    employment_type = Column(String(25), default='main')  # main, part_time
    degree = Column(String(40), default='higher')
    qualification = Column(String(30), default='none')  # top, first, second, none
    qualification_valid_until = Column(Date, nullable=True)
    national_certificate = Column(Boolean, default=False)
    certificate_valid_until = Column(Date, nullable=True)
    retraining_diploma = Column(Boolean, default=False)
    priority_basis = Column(String(35), default='higher_none')
    priority_evidence = Column(String(350), default='')
    primary_specialist = Column(Boolean, default=False)
    base_salary = Column(Numeric(14, 2), default=0)
    hire_date = Column(Date, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)
    school = relationship('School')

class EmployeeSubject(Base):
    __tablename__ = 'employee_subjects'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    primary_methodology = Column(Boolean, default=False)
    qualification_note = Column(String(260), default='')
    __table_args__ = (UniqueConstraint('employee_id','subject_id', name='uq_employee_subject'),)
    employee = relationship('Employee')
    subject = relationship('Subject')

class ClassGroup(Base):
    __tablename__ = 'class_groups'
    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False, index=True)
    year_id = Column(Integer, ForeignKey('academic_years.id'), nullable=False)
    grade = Column(Integer, nullable=False)
    section = Column(String(8), nullable=False)
    student_count = Column(Integer, nullable=False)
    language = Column(String(30), default='uz')
    approved = Column(Boolean, default=False)
    __table_args__ = (UniqueConstraint('school_id','year_id','grade','section','language',name='uq_class_group'),)
    year = relationship('AcademicYear')

class CurriculumLine(Base):
    __tablename__ = 'curriculum_lines'
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey('class_groups.id'), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    weekly_hours = Column(Float, nullable=False)
    groups = Column(Integer, default=1, nullable=False)
    source_ref = Column(String(320), default='')
    verified = Column(Boolean, default=False)
    __table_args__ = (UniqueConstraint('class_id','subject_id',name='uq_class_subject'),)
    klass = relationship('ClassGroup')
    subject = relationship('Subject')
    @property
    def total_hours(self):
        return round(self.weekly_hours * self.groups, 2)

class CouncilDecision(Base):
    __tablename__ = 'council_decisions'
    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    year_id = Column(Integer, ForeignKey('academic_years.id'), nullable=False)
    number = Column(String(80), nullable=False)
    date = Column(Date, nullable=False)
    kind = Column(String(30), default='hours') # hours, bonus
    document_ref = Column(String(300), default='')
    approved = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=now)

class Allocation(Base):
    __tablename__ = 'allocations'
    id = Column(Integer, primary_key=True)
    line_id = Column(Integer, ForeignKey('curriculum_lines.id'), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False, index=True)
    weekly_hours = Column(Float, nullable=False)
    state = Column(String(25), default='draft')  # draft, approved, superseded (historical FK remains)
    decision_id = Column(Integer, ForeignKey('council_decisions.id'), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=now)
    line = relationship('CurriculumLine')
    employee = relationship('Employee')
    decision = relationship('CouncilDecision')

class HourChangeRequest(Base):
    __tablename__ = 'hour_change_requests'
    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    requester_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    source_allocation_id = Column(Integer, ForeignKey('allocations.id'), nullable=False)
    target_employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    target_allocation_id = Column(Integer, ForeignKey('allocations.id'), nullable=True) # swap
    request_type = Column(String(20), nullable=False) # transfer / swap
    weekly_hours = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    recipient_consented = Column(Boolean, default=False)
    status = Column(String(22), default='pending') # pending, approved, rejected
    council_decision_id = Column(Integer, ForeignKey('council_decisions.id'), nullable=True)
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    manager_note = Column(Text, default='')
    created_at = Column(DateTime, default=now)
    decided_at = Column(DateTime, nullable=True)

class BonusPeriod(Base):
    __tablename__ = 'bonus_periods'
    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    year_id = Column(Integer, ForeignKey('academic_years.id'), nullable=False)
    name = Column(String(80), nullable=False)
    fund_limit = Column(Numeric(15,2), default=0)
    group_member_count = Column(Integer, default=0)
    group_protocol = Column(String(250), default='')
    status = Column(String(25), default='draft')
    created_at = Column(DateTime, default=now)
    __table_args__ = (UniqueConstraint('school_id','year_id','name',name='uq_bonus_period'),)

class BonusAssessment(Base):
    __tablename__ = 'bonus_assessments'
    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey('bonus_periods.id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    score = Column(Float, nullable=False)
    evidence = Column(Text, default='')
    rate = Column(Float, default=0)
    amount = Column(Numeric(14,2), default=0)
    state = Column(String(22), default='draft')
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    __table_args__ = (UniqueConstraint('period_id','employee_id',name='uq_bonus_assessment'),)

class PolicyVersion(Base):
    __tablename__ = 'policy_versions'
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    valid_from = Column(Date, nullable=False)
    source_url = Column(String(350), nullable=False)
    params = Column(JSON, default=dict)
    locked = Column(Boolean, default=True)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    actor_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=True)
    action = Column(String(110), nullable=False)
    entity = Column(String(70), default='')
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, default='')
    at = Column(DateTime, default=now)

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(String(400), default='')
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=now)

class BonusCriterion(Base):
    __tablename__ = 'bonus_criteria'
    id = Column(Integer, primary_key=True)
    code = Column(String(70), nullable=False)
    scheme = Column(String(35), default='teacher')
    name = Column(String(250), nullable=False)
    max_score = Column(Float, nullable=False)
    source_clause = Column(String(250), default='')
    valid_from = Column(Date, nullable=True)
    active = Column(Boolean, default=True)
    __table_args__ = (UniqueConstraint('code','scheme',name='uq_bonus_criterion'),)

class BonusCriterionScore(Base):
    __tablename__ = 'bonus_criterion_scores'
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('bonus_assessments.id'), nullable=False)
    criterion_id = Column(Integer, ForeignKey('bonus_criteria.id'), nullable=False)
    score = Column(Float, nullable=False)
    evidence_ref = Column(String(350), default='')
    verified_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    __table_args__ = (UniqueConstraint('assessment_id','criterion_id',name='uq_criterion_score'),)

class BonusMeeting(Base):
    __tablename__ = 'bonus_meetings'
    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey('bonus_periods.id'), nullable=False)
    held_on = Column(Date, nullable=False)
    protocol_ref = Column(String(350), nullable=False)
    attendees = Column(Integer, nullable=False)
    labor_union_present = Column(Boolean, nullable=False)
    parent_present = Column(Boolean, nullable=False)
    supervisory_board_present = Column(Boolean, nullable=False)
    votes_for = Column(Integer, nullable=False)
    votes_against = Column(Integer, nullable=False)
    votes_abstain = Column(Integer, default=0)
    director_order_ref = Column(String(350), nullable=False)
    recorded_by = Column(Integer, ForeignKey('users.id'), nullable=False)
