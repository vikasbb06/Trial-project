from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import TeacherCreate, TeacherResponse, LoginRequest, Token
import models
from auth_utils import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=TeacherResponse, status_code=201)
def register(data: TeacherCreate, db: Session = Depends(get_db)):
    if db.query(models.Teacher).filter(models.Teacher.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    teacher = models.Teacher(
        name=data.name,
        email=data.email,
        password=hash_password(data.password)
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher

@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.email == data.email).first()
    if not teacher or not verify_password(data.password, teacher.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": teacher.email})
    return {"access_token": token}
