"""Read-only, school/year-scoped curriculum matrix.

Adapted as a secure, DB-backed view from darstaqsimot's CurriculumModule
and DistributionModule concepts.  This module does NOT assign lessons or
validate that a school's curriculum matches an official ministerial plan.
"""
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from .models import Allocation, ClassGroup, CurriculumLine

ACTIVE_STATES = ('draft', 'approved')


def school_curriculum_matrix(db: Session, school_id: int, year_id: int, grade: int | None = None) -> dict:
    """Build class×subject cells while keeping learning and teacher hours separate.

    All queries are scoped to both school and academic year. Draft allocations
    reserve capacity for a provisional distribution; superseded records don't.
    No database writes happen here.
    """
    class_stmt = (select(ClassGroup)
                  .where(ClassGroup.school_id == school_id, ClassGroup.year_id == year_id)
                  .order_by(ClassGroup.grade, ClassGroup.section, ClassGroup.language, ClassGroup.id))
    if grade is not None:
        class_stmt = class_stmt.where(ClassGroup.grade == grade)
    classes = list(db.scalars(class_stmt).all())
    class_ids = [c.id for c in classes]
    class_by_id = {c.id: c for c in classes}
    empty = {'classes': [], 'subjects': [], 'totals': {
        'class_count': 0, 'subject_count': 0, 'learning_hours': 0.0,
        'teacher_hours': 0.0, 'allocated_hours': 0.0,
        'approved_hours': 0.0, 'remaining_hours': 0.0,
        'unverified_lines': 0, 'grouped_lines': 0,
        'primary_teacher_hours': 0.0, 'upper_teacher_hours': 0.0,
    }, 'subject_totals': [], 'records': []}
    if not classes:
        return empty

    lines = list(db.scalars(select(CurriculumLine)
                .options(selectinload(CurriculumLine.subject))
                .where(CurriculumLine.class_id.in_(class_ids))
                .order_by(CurriculumLine.class_id, CurriculumLine.subject_id)).all())
    line_ids = [line.id for line in lines]
    allocations = list(db.scalars(select(Allocation).where(
        Allocation.line_id.in_(line_ids), Allocation.state.in_(ACTIVE_STATES))).all()) if line_ids else []
    by_line = defaultdict(lambda: {'draft': 0.0, 'approved': 0.0})
    for allocation in allocations:
        by_line[allocation.line_id][allocation.state] += float(allocation.weekly_hours)

    subjects_by_id = {line.subject.id: line.subject for line in lines}
    subjects = sorted(subjects_by_id.values(), key=lambda sub: (sub.name.casefold(), sub.id))
    ordered_subject_ids = [sub.id for sub in subjects]
    cells = {}
    records = []
    subject_sums = defaultdict(lambda: {'learning_hours': 0.0, 'teacher_hours': 0.0,
                                        'allocated_hours': 0.0, 'remaining_hours': 0.0})
    totals = dict(empty['totals'])
    totals['class_count'] = len(classes)
    totals['subject_count'] = len(subjects)
    for line in lines:
        klass = class_by_id[line.class_id]
        learning = round(float(line.weekly_hours), 2)
        teaching = round(float(line.total_hours), 2)
        draft = round(by_line[line.id]['draft'], 2)
        approved = round(by_line[line.id]['approved'], 2)
        assigned = round(draft + approved, 2)
        remaining = round(max(0.0, teaching - assigned), 2)
        over = round(max(0.0, assigned - teaching), 2)
        cell = {'line_id': line.id, 'class_id': klass.id, 'grade': klass.grade,
                'section': klass.section, 'language': klass.language,
                'class_label': f'{klass.grade}-{klass.section}',
                'subject_id': line.subject_id, 'subject_name': line.subject.name,
                'learning_hours': learning, 'groups': line.groups, 'teacher_hours': teaching,
                'draft_hours': draft, 'approved_hours': approved,
                'allocated_hours': assigned, 'remaining_hours': remaining,
                'overallocated_hours': over, 'verified': bool(line.verified and klass.approved),
                'source_ref': line.source_ref or ''}
        cells[(klass.id, line.subject_id)] = cell
        records.append(cell)
        for key, value in [('learning_hours', learning), ('teacher_hours', teaching),
                           ('allocated_hours', assigned), ('approved_hours', approved),
                           ('remaining_hours', remaining)]:
            totals[key] += value
            if key in subject_sums[line.subject_id]:
                subject_sums[line.subject_id][key] += value
        totals['unverified_lines'] += 0 if cell['verified'] else 1
        totals['grouped_lines'] += 1 if line.groups > 1 else 0
        group_key = 'primary_teacher_hours' if klass.grade <= 4 else 'upper_teacher_hours'
        totals[group_key] += teaching
    result_classes = []
    for klass in classes:
        klass_cells = [cells.get((klass.id, sub_id)) for sub_id in ordered_subject_ids]
        present = [cell for cell in klass_cells if cell]
        result_classes.append({
            'id': klass.id, 'grade': klass.grade, 'section': klass.section,
            'language': klass.language, 'student_count': klass.student_count,
            'approved': bool(klass.approved), 'label': f'{klass.grade}-{klass.section}',
            'cells': klass_cells,
            'learning_hours': round(sum(c['learning_hours'] for c in present), 2),
            'teacher_hours': round(sum(c['teacher_hours'] for c in present), 2),
            'allocated_hours': round(sum(c['allocated_hours'] for c in present), 2),
            'remaining_hours': round(sum(c['remaining_hours'] for c in present), 2),
        })
    for key in totals:
        if isinstance(totals[key], float): totals[key] = round(totals[key], 2)
    return {
        'classes': result_classes, 'subjects': subjects, 'records': records,
        'totals': totals,
        'subject_totals': [dict(subject_id=s.id, name=s.name,
                           **{k: round(v, 2) for k, v in subject_sums[s.id].items()})
                           for s in subjects],
    }
