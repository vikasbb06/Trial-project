# Student Result Analysis & Attendance Management System

A FastAPI backend for managing student results and attendance.

## Project Structure

```
student_system/
├── main.py            # App entry point
├── database.py        # DB engine & session
├── models.py          # SQLAlchemy ORM models
├── schemas.py         # Pydantic request/response schemas
├── auth_utils.py      # JWT auth helpers
├── requirements.txt
└── routers/
    ├── auth.py        # Register / Login
    ├── students.py    # Student CRUD
    ├── subjects.py    # Subject CRUD
    ├── attendance.py  # Mark & analyse attendance
    └── results.py     # Enter marks & analytics
```

## Setup & Run

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
uvicorn main:app --reload
```

Server runs at: http://localhost:8000  
Interactive API docs: http://localhost:8000/docs

## API Overview

### Auth
| Method | Endpoint              | Description        |
|--------|-----------------------|--------------------|
| POST   | /api/auth/register    | Register a teacher |
| POST   | /api/auth/login       | Login → get token  |

> All other endpoints require `Authorization: Bearer <token>` header.

### Students
| Method | Endpoint                  | Description         |
|--------|---------------------------|---------------------|
| POST   | /api/students/            | Add student         |
| GET    | /api/students/            | List all (filter by class) |
| GET    | /api/students/{id}        | Get student         |
| PUT    | /api/students/{id}        | Update student      |
| DELETE | /api/students/{id}        | Delete student      |

### Subjects
| Method | Endpoint                  | Description     |
|--------|---------------------------|-----------------|
| POST   | /api/subjects/            | Add subject     |
| GET    | /api/subjects/            | List subjects   |
| DELETE | /api/subjects/{id}        | Delete subject  |

### Attendance
| Method | Endpoint                          | Description                    |
|--------|-----------------------------------|--------------------------------|
| POST   | /api/attendance/                  | Mark single attendance         |
| POST   | /api/attendance/bulk              | Mark attendance for whole class|
| GET    | /api/attendance/                  | List records (filterable)      |
| GET    | /api/attendance/summary           | Per-student % summary          |
| GET    | /api/attendance/low-attendance    | Students below threshold (75%) |

### Results
| Method | Endpoint                                  | Description              |
|--------|-------------------------------------------|--------------------------|
| POST   | /api/results/                             | Add/update marks         |
| GET    | /api/results/                             | List results             |
| GET    | /api/results/student/{id}                 | Full result card + grade |
| GET    | /api/results/class/{class_name}/analytics | Class-wide analytics     |

## Grade Scale
| % Range | Grade |
|---------|-------|
| 90–100  | A+    |
| 80–89   | A     |
| 70–79   | B+    |
| 60–69   | B     |
| 50–59   | C     |
| 40–49   | D     |
| < 40    | F     |

## Git Setup

```bash
git init
git add .
git commit -m "Initial commit: Student Result & Attendance Management backend"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```
