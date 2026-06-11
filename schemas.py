from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date
from models import AttendanceStatus


# ── Auth ────────────────────────────────────────────────────────────────────

class TeacherCreate(BaseModel):
    name:     str
    email:    EmailStr
    password: str

class TeacherResponse(BaseModel):
    id:    int
    name:  str
    email: EmailStr
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type:   str = "bearer"


# ── Student ─────────────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    roll_number: str
    name:        str
    email:       Optional[EmailStr] = None
    class_name:  str

class StudentUpdate(BaseModel):
    name:       Optional[str]       = None
    email:      Optional[EmailStr]  = None
    class_name: Optional[str]       = None

class StudentResponse(BaseModel):
    id:          int
    roll_number: str
    name:        str
    email:       Optional[str]
    class_name:  str
    class Config:
        from_attributes = True


# ── Subject ─────────────────────────────────────────────────────────────────

class SubjectCreate(BaseModel):
    name:       str
    code:       str
    max_marks:  int = 100
    pass_marks: int = 35

class SubjectResponse(BaseModel):
    id:         int
    name:       str
    code:       str
    max_marks:  int
    pass_marks: int
    class Config:
        from_attributes = True


# ── Attendance ───────────────────────────────────────────────────────────────

class AttendanceCreate(BaseModel):
    student_id: int
    date:       date
    status:     AttendanceStatus

class AttendanceBulkCreate(BaseModel):
    date:    date
    records: List[dict]  # [{"student_id": 1, "status": "present"}, ...]

class AttendanceResponse(BaseModel):
    id:         int
    student_id: int
    date:       date
    status:     AttendanceStatus
    class Config:
        from_attributes = True

class AttendanceSummary(BaseModel):
    student_id:       int
    student_name:     str
    roll_number:      str
    total_days:       int
    present:          int
    absent:           int
    late:             int
    attendance_pct:   float


# ── Results ──────────────────────────────────────────────────────────────────

class ResultCreate(BaseModel):
    student_id: int
    subject_id: int
    marks:      float
    exam_type:  str = "Final"

class ResultResponse(BaseModel):
    id:           int
    student_id:   int
    subject_id:   int
    marks:        float
    exam_type:    str
    class Config:
        from_attributes = True

class StudentResultSummary(BaseModel):
    student_id:   int
    student_name: str
    roll_number:  str
    class_name:   str
    subjects:     List[dict]   # [{name, marks, max_marks, pass_marks, grade, status}]
    total_marks:  float
    total_max:    float
    percentage:   float
    overall_grade: str
    result_status: str          # Pass / Fail

class ClassAnalytics(BaseModel):
    class_name:    str
    total_students: int
    passed:        int
    failed:        int
    pass_rate:     float
    class_avg_pct: float
    subject_averages: List[dict]
    toppers:       List[dict]
