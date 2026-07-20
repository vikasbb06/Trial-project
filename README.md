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
