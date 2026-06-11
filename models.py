from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class Teacher(Base):
    __tablename__ = "teachers"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    email      = Column(String, unique=True, index=True, nullable=False)
    password   = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Student(Base):
    __tablename__ = "students"

    id           = Column(Integer, primary_key=True, index=True)
    roll_number  = Column(String, unique=True, index=True, nullable=False)
    name         = Column(String, nullable=False)
    email        = Column(String, unique=True, index=True)
    class_name   = Column(String, nullable=False)   # e.g. "10A", "11B"
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    attendance_records = relationship("Attendance", back_populates="student")
    result_records     = relationship("Result",     back_populates="student")


class Subject(Base):
    __tablename__ = "subjects"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    code       = Column(String, unique=True, index=True, nullable=False)
    max_marks  = Column(Integer, default=100)
    pass_marks = Column(Integer, default=35)

    result_records = relationship("Result", back_populates="subject")


class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent  = "absent"
    late    = "late"


class Attendance(Base):
    __tablename__ = "attendance"

    id         = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date       = Column(Date, nullable=False)
    status     = Column(Enum(AttendanceStatus), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="attendance_records")


class Result(Base):
    __tablename__ = "results"

    id         = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    marks      = Column(Float, nullable=False)
    exam_type  = Column(String, default="Final")   # Midterm, Final, Unit Test
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="result_records")
    subject = relationship("Subject", back_populates="result_records")
