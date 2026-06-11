from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from schemas import ResultCreate, ResultResponse, StudentResultSummary, ClassAnalytics
from auth_utils import get_current_teacher
import models

router = APIRouter()


def calculate_grade(percentage: float) -> str:
    if percentage >= 90: return "A+"
    if percentage >= 80: return "A"
    if percentage >= 70: return "B+"
    if percentage >= 60: return "B"
    if percentage >= 50: return "C"
    if percentage >= 40: return "D"
    else:return "F"


@router.post("/", response_model=ResultResponse, status_code=201)
def add_result(
    data: ResultCreate,
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    subject = db.query(models.Subject).filter(models.Subject.id == data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    if data.marks > subject.max_marks:
        raise HTTPException(
            status_code=400,
            detail=f"Marks ({data.marks}) cannot exceed max marks ({subject.max_marks})"
        )

    # Update if exists for same student+subject+exam_type
    existing = db.query(models.Result).filter(
        models.Result.student_id == data.student_id,
        models.Result.subject_id == data.subject_id,
        models.Result.exam_type  == data.exam_type
    ).first()
    if existing:
        existing.marks = data.marks
        db.commit()
        db.refresh(existing)
        return existing

    result = models.Result(**data.model_dump())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("/student/{student_id}", response_model=StudentResultSummary)
def student_result_summary(
    student_id: int,
    exam_type:  Optional[str] = "Final",
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    results = db.query(models.Result).filter(
        models.Result.student_id == student_id,
        models.Result.exam_type  == exam_type
    ).all()

    subjects_detail = []
    total_marks = 0.0
    total_max   = 0.0
    passed_all  = True

    for r in results:
        pct   = round((r.marks / r.subject.max_marks) * 100, 2)
        grade = calculate_grade(pct)
        passed = r.marks >= r.subject.pass_marks
        if not passed:
            passed_all = False
        subjects_detail.append({
            "subject_id":   r.subject_id,
            "subject_name": r.subject.name,
            "subject_code": r.subject.code,
            "marks":        r.marks,
            "max_marks":    r.subject.max_marks,
            "pass_marks":   r.subject.pass_marks,
            "percentage":   pct,
            "grade":        grade,
            "status":       "Pass" if passed else "Fail"
        })
        total_marks += r.marks
        total_max   += r.subject.max_marks

    overall_pct   = round((total_marks / total_max * 100), 2) if total_max > 0 else 0.0
    overall_grade = calculate_grade(overall_pct)

    return StudentResultSummary(
        student_id=student.id,
        student_name=student.name,
        roll_number=student.roll_number,
        class_name=student.class_name,
        subjects=subjects_detail,
        total_marks=total_marks,
        total_max=total_max,
        percentage=overall_pct,
        overall_grade=overall_grade,
        result_status="Pass" if passed_all and len(results) > 0 else "Fail"
    )


@router.get("/class/{class_name}/analytics", response_model=ClassAnalytics)
def class_analytics(
    class_name: str,
    exam_type:  Optional[str] = "Final",
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    students = db.query(models.Student).filter(
        models.Student.class_name == class_name
    ).all()

    if not students:
        raise HTTPException(status_code=404, detail="No students found for this class")

    passed        = 0
    failed        = 0
    class_pct_sum = 0.0
    subject_marks: dict = {}   # subject_id -> {"name": ..., "total": ..., "count": ...}
    student_scores: list = []

    for student in students:
        results = db.query(models.Result).filter(
            models.Result.student_id == student.id,
            models.Result.exam_type  == exam_type
        ).all()

        total_marks = sum(r.marks for r in results)
        total_max   = sum(r.subject.max_marks for r in results)
        pct         = round((total_marks / total_max * 100), 2) if total_max > 0 else 0.0
        passed_all  = all(r.marks >= r.subject.pass_marks for r in results)

        if passed_all and len(results) > 0:
            passed += 1
        else:
            failed += 1

        class_pct_sum += pct
        student_scores.append({
            "student_id":   student.id,
            "student_name": student.name,
            "roll_number":  student.roll_number,
            "percentage":   pct,
            "grade":        calculate_grade(pct)
        })

        for r in results:
            if r.subject_id not in subject_marks:
                subject_marks[r.subject_id] = {
                    "subject_name": r.subject.name,
                    "total":        0.0,
                    "max_marks":    r.subject.max_marks,
                    "count":        0
                }
            subject_marks[r.subject_id]["total"] += r.marks
            subject_marks[r.subject_id]["count"] += 1

    total_students   = len(students)
    class_avg_pct    = round(class_pct_sum / total_students, 2) if total_students > 0 else 0.0
    pass_rate        = round((passed / total_students * 100), 2) if total_students > 0 else 0.0

    subject_averages = [
        {
            "subject_id":   sid,
            "subject_name": v["subject_name"],
            "average_marks": round(v["total"] / v["count"], 2) if v["count"] else 0,
            "max_marks":    v["max_marks"],
            "average_pct":  round((v["total"] / v["count"] / v["max_marks"] * 100), 2)
                            if v["count"] else 0
        }
        for sid, v in subject_marks.items()
    ]

    toppers = sorted(student_scores, key=lambda x: x["percentage"], reverse=True)[:5]

    return ClassAnalytics(
        class_name=class_name,
        total_students=total_students,
        passed=passed,
        failed=failed,
        pass_rate=pass_rate,
        class_avg_pct=class_avg_pct,
        subject_averages=subject_averages,
        toppers=toppers
    )


@router.get("/", response_model=List[ResultResponse])
def list_results(
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    exam_type:  Optional[str] = None,
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    query = db.query(models.Result)
    if student_id:
        query = query.filter(models.Result.student_id == student_id)
    if subject_id:
        query = query.filter(models.Result.subject_id == subject_id)
    if exam_type:
        query = query.filter(models.Result.exam_type == exam_type)
    return query.all()
