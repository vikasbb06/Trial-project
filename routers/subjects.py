from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import SubjectCreate, SubjectResponse
from auth_utils import get_current_teacher
import models

router = APIRouter()

@router.post("/", response_model=SubjectResponse, status_code=201)
def create_subject(
    data: SubjectCreate,
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    if db.query(models.Subject).filter(models.Subject.code == data.code).first():
        raise HTTPException(status_code=400, detail="Subject code already exists")
    subject = models.Subject(**data.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@router.get("/", response_model=List[SubjectResponse])
def list_subjects(
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    return db.query(models.Subject).order_by(models.Subject.name).all()

@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.delete("/{subject_id}", status_code=204)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _: models.Teacher = Depends(get_current_teacher)
):
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject)
    db.commit()
