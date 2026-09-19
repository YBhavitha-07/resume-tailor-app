from pydantic import BaseModel


class ResumeAnalysisInput(BaseModel):
    resume_text: str
    job_description: str


class ResumeAnalysisOutput(BaseModel):
    ats_score: int
    match_percentage: int
    missing_keywords: list[str]
    suggestions: list[str]
    tailored_resume: str
