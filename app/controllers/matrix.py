"""Read-only school admin curriculum matrix and safe spreadsheet export."""
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from ..db import get_db
from ..ui import admin, page
from ..curriculum_matrix import school_curriculum_matrix
from .school import active_year

router = APIRouter(prefix='/school')


def _context(request: Request, db: Session, grade: int | None):
    user = admin(request, db)
    if grade is not None and not 1 <= grade <= 11:
        raise HTTPException(400, 'Sinf 1 dan 11 gacha')
    year = active_year(db)
    return user, year, school_curriculum_matrix(db, user.school_id, year.id, grade)


@router.get('/matrix')
def matrix(request: Request, grade: int | None = Query(default=None), db: Session = Depends(get_db)):
    user, year, data = _context(request, db, grade)
    return page(request, 'matrix.html', db, matrix=data, selected_grade=grade, year=year)


def safe_csv(value):
    """Avoid spreadsheet formula execution via CSV cells."""
    text = str(value if value is not None else '')
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')) else text


@router.get('/matrix/export.csv')
def matrix_export(request: Request, grade: int | None = Query(default=None), db: Session = Depends(get_db)):
    user, year, data = _context(request, db, grade)
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(['Sinf', 'Ta’lim tili', 'Fan', 'O‘quv soati (hafta)', 'Guruhlar',
                     'O‘qituvchi soati (hafta)', 'Loyiha soati', 'Tasdiqlangan soat',
                     'Jami taqsimlangan', 'Taqsimlanmagan', 'Setka tekshirildi', 'Manba'])
    for cell in data['records']:
        writer.writerow([safe_csv(cell['class_label']), safe_csv(cell['language']),
             safe_csv(cell['subject_name']), cell['learning_hours'], cell['groups'],
             cell['teacher_hours'], cell['draft_hours'], cell['approved_hours'],
             cell['allocated_hours'], cell['remaining_hours'],
             'Ha' if cell['verified'] else 'Yo‘q', safe_csv(cell['source_ref'])])
    payload = ('\ufeff' + stream.getvalue()).encode('utf-8')
    return Response(payload, media_type='text/csv; charset=utf-8', headers={
        'Content-Disposition': f'attachment; filename="edutarif-matrix-school-{user.school_id}-year-{year.id}.csv"',
        'Cache-Control': 'no-store'})
