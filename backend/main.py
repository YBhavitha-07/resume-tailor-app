import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from ai_service import rewrite_resume_bullets
from ats_analyzer import analyze_resume, generate_recruiter_view
from pdf_generator import generate_resume_pdf
from resume_parser import extract_resume_text

load_dotenv()

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

app = FastAPI(title="AI Resume Tailor & ATS Score Checker", version="1.0.0")
max_upload_bytes = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10")) * 1024 * 1024

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    resume_text: str = Field(..., min_length=50)
    job_description: str = Field(..., min_length=50)

    @field_validator("resume_text", "job_description")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text cannot be empty.")
        return value


class RewriteRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    resume_text: str = Field(..., min_length=50)
    job_description: str = Field(..., min_length=50)
    target_bullet: str | None = None
    tone: str = "professional"


class RecruiterViewRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    resume_text: str = Field(..., min_length=50)
    job_description: str = Field(..., min_length=50)


class PdfRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(..., min_length=20)
    title: str = Field(default="Tailored Resume")


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(_, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": f"Internal server error: {str(exc)}"})


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "AI Resume Tailor & ATS Score Checker"}


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected.")

    file_extension = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = {".pdf", ".docx"}
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(file_bytes) > max_upload_bytes:
        raise HTTPException(status_code=413, detail=f"Uploaded file exceeds the {max_upload_bytes / (1024 * 1024):.0f}MB limit.")

    try:
        extracted_text = extract_resume_text(file.filename, file_bytes)
        detected_sections = []
        if extracted_text.strip():
            from resume_parser import detect_resume_sections

            detected_sections = detect_resume_sections(extracted_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(exc)}") from exc

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Resume uploaded and parsed successfully.",
        "extracted_text": extracted_text,
        "detected_sections": detected_sections,
    }


@app.post("/analyze")
def analyze(payload: AnalyzeRequest):
    try:
        result = analyze_resume(payload.resume_text, payload.job_description)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(exc)}") from exc


@app.post("/rewrite")
def rewrite(payload: RewriteRequest):
    try:
        result = rewrite_resume_bullets(
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            target_bullet=payload.target_bullet,
            tone=payload.tone,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Rewrite failed: {str(exc)}") from exc


@app.post("/recruiter-view")
def recruiter_view(payload: RecruiterViewRequest):
    try:
        return generate_recruiter_view(payload.resume_text, payload.job_description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recruiter view failed: {str(exc)}") from exc


@app.post("/generate-pdf")
def generate_pdf(payload: PdfRequest):
    try:
        pdf_bytes = generate_resume_pdf(payload.content, title=payload.title)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(exc)}") from exc

    file_name = f"{(payload.title or 'resume').replace(' ', '_').lower()}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )
