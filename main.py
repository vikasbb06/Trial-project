from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, students, subjects, attendance, results

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Result & Attendance Management API",
    description="Backend API for managing student results and attendance",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,       prefix="/api/auth",       tags=["Authentication"])
app.include_router(students.router,   prefix="/api/students",   tags=["Students"])
app.include_router(subjects.router,   prefix="/api/subjects",   tags=["Subjects"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(results.router,    prefix="/api/results",    tags=["Results"])

@app.get("/")
def root():
    return {"message": "Student Management System API is running"}
