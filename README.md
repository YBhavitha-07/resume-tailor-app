<<<<<<< HEAD
# AI Resume Tailor & ATS Score Checker

This project is split into a React + Vite frontend and a Python + FastAPI backend.

## Project structure

- `frontend/` - React application for the user interface
- `backend/` - FastAPI API for ATS scoring and resume tailoring

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Default ports

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

## Features planned

- Resume text input
- Job description input
- ATS keyword matching analysis
- Missing keyword suggestions
- Resume tailoring assistance
=======
# resume-tailor-app
AI-powered Resume Tailor application
>>>>>>> 2ab58f0d949e420f8d06eba89e937895af55629d
