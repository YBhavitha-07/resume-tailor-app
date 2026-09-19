from fastapi import APIRouter

from app.schemas.resume import ResumeAnalysisInput, ResumeAnalysisOutput
from app.services.ats_checker import analyze_resume_match
from app.services.resume_tailor import tailor_resume

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.post("/analyze", response_model=ResumeAnalysisOutput)
def analyze_resume(payload: ResumeAnalysisInput):
    analysis = analyze_resume_match(payload.resume_text, payload.job_description)
    tailored = tailor_resume(payload.resume_text, payload.job_description)

    return {
        "ats_score": analysis["ats_score"],
        "match_percentage": analysis["match_percentage"],
        "missing_keywords": analysis["missing_keywords"],
        "suggestions": analysis["suggestions"],
        "tailored_resume": tailored,
    }


@router.post("/tailor")
def tailor_resume_for_job(payload: ResumeAnalysisInput):
    return {
        "tailored_resume": tailor_resume(payload.resume_text, payload.job_description)
    }
