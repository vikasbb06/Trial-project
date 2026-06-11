from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
from database import get_db
from schemas import AttendanceCreate, AttendanceBulkCreate, AttendanceResponse, AttendanceSummary
from auth_utils import get_current_teacher
from models import AttendanceStatus
import models

router = APIRouter()


@router.post("/", response_model=AttendanceResponse, status_code=201)
def mark_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    # Prevent duplicate entry for same student+date
    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == data.student_id,
        models.Attendance.date == data.date
    ).first()
    if existing:
        # Update instead of error
        existing.status = data.status
        db.commit()
        db.refresh(existing)
        return existing

    record = models.Attendance(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/bulk", status_code=201)
def mark_bulk_attendance(
    data: AttendanceBulkCreate,
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    """Mark attendance for multiple students on the same date at once."""
    created = 0
    updated = 0
    for rec in data.records:
        student_id = rec.get("student_id")
        status     = rec.get("status")
        if not student_id or not status:
            continue
        existing = db.query(models.Attendance).filter(
            models.Attendance.student_id == student_id,
            models.Attendance.date == data.date
        ).first()
        if existing:
            existing.status = status
            updated += 1
        else:
            db.add(models.Attendance(student_id=student_id, date=data.date, status=status))
            created += 1
    db.commit()
    return {"created": created, "updated": updated, "date": data.date}


@router.get("/", response_model=List[AttendanceResponse])
def get_attendance(
    student_id: Optional[int]  = None,
    date_from:  Optional[date] = None,
    date_to:    Optional[date] = None,
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    query = db.query(models.Attendance)
    if student_id:
        query = query.filter(models.Attendance.student_id == student_id)
    if date_from:
        query = query.filter(models.Attendance.date >= date_from)
    if date_to:
        query = query.filter(models.Attendance.date <= date_to)
    return query.order_by(models.Attendance.date.desc()).all()


@router.get("/summary", response_model=List[AttendanceSummary])
def attendance_summary(
    class_name: Optional[str]  = None,
    date_from:  Optional[date] = None,
    date_to:    Optional[date] = None,
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    """Per-student attendance summary with percentage."""
    student_query = db.query(models.Student)
    if class_name:
        student_query = student_query.filter(models.Student.class_name == class_name)
    students = student_query.all()

    summaries = []
    for student in students:
        att_query = db.query(models.Attendance).filter(
            models.Attendance.student_id == student.id
        )
        if date_from:
            att_query = att_query.filter(models.Attendance.date >= date_from)
        if date_to:
            att_query = att_query.filter(models.Attendance.date <= date_to)

        records    = att_query.all()
        total_days = len(records)
        present    = sum(1 for r in records if r.status == AttendanceStatus.present)
        absent     = sum(1 for r in records if r.status == AttendanceStatus.absent)
        late       = sum(1 for r in records if r.status == AttendanceStatus.late)
        pct        = round((present / total_days * 100), 2) if total_days > 0 else 0.0

        summaries.append(AttendanceSummary(
            student_id=student.id,
            student_name=student.name,
            roll_number=student.roll_number,
            total_days=total_days,
            present=present,
            absent=absent,
            late=late,
            attendance_pct=pct
        ))
    return summaries


@router.get("/low-attendance", response_model=List[AttendanceSummary])
def low_attendance_alert(
    threshold:  float          = 75.0,
    class_name: Optional[str]  = None,
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    """Return students whose attendance % is below the threshold (default 75%)."""
    all_summaries = attendance_summary(class_name=class_name, db=db, _=_)
    return [s for s in all_summaries if s.attendance_pct < threshold]
