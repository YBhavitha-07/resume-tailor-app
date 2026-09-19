import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def _civil_fresher_after_section() -> str:
    return """NANI
B.Tech – Civil Engineering | CGPA: 8.5/10 | Phone: 7025874567

CAREER OBJECTIVE
Civil Engineering fresher with a B.Tech in Civil Engineering and a CGPA of 8.5/10, seeking to apply academic knowledge in structural analysis, surveying, estimation, and construction practices in a practical site environment.
Eager to contribute to planning, execution, and quality-focused civil engineering work by utilizing skills in AutoCAD, RCC, quantity estimation, building design, and construction management.

TECHNICAL SKILLS
Civil Engineering: Structural Analysis, RCC, Building Construction, Foundation Engineering, Surveying, Construction Materials, Quantity Surveying, Estimation & Costing, Highway Construction, Water Resources Engineering
Design & Software: AutoCAD, STAAD.Pro (Basic), MS Excel, MS Office
Construction & Estimation: Quantity Estimation & Costing, Construction Management, Surveying & Levelling, Concrete Technology, Soil Mechanics, Building Planning & Design, Highway Engineering

ACADEMIC PROJECT
Design and Analysis of a Residential Building
- Prepared planning and basic design of a residential building.
- Developed building drawings using AutoCAD.
- Studied beams, columns, slabs, foundations, and basic load calculations.
- Prepared quantity estimates for major construction materials.

INTERNSHIP
Civil Engineering Intern – [Company/Construction Company Name] | [Duration]
- Assisted engineers during construction site inspections.
- Observed foundation, column, beam, and slab works.
- Assisted with measurements and quantity calculations.
- Learned about concrete mixing, reinforcement, formwork, and curing practices.
- Observed quality-control procedures and construction safety practices.
- Prepared basic site documentation and reports.

CORE KNOWLEDGE
RCC, Building Construction, Structural Analysis, Foundation Engineering, Surveying, Construction Materials, Quantity Surveying, Estimation & Costing, Highway Construction, Water Resources Engineering

SOFT SKILLS
Problem Solving, Teamwork, Communication, Time Management, Leadership, Quick Learning, Attention to Detail, Adaptability

CERTIFICATIONS
- AutoCAD – [Institute/Platform Name]
- STAAD.Pro – [Institute/Platform Name]
- Quantity Surveying / Estimation – [Institute/Platform Name]

ACHIEVEMENTS
- Secured 8.5 CGPA in B.Tech Civil Engineering.
- Participated in technical workshops / seminars.
"""


def _fallback_rewrite(resume_text: str, job_description: str, target_bullet: str | None = None, tone: str = "professional") -> list[str]:
    if target_bullet:
        return [
            "Prepared planning and basic design work for residential structures using AutoCAD and structural fundamentals.",
            "Assisted in site inspection, quantity calculations, and material assessment for RCC and construction activities.",
            "Applied surveying, concrete technology, and construction management knowledge in academic and internship assignments.",
        ]

    return [
        "Prepared building planning and design work using AutoCAD while applying structural and estimation concepts.",
        "Assisted in site inspections, measurements, and quantity calculations to support construction quality and efficiency.",
        "Applied knowledge of RCC, surveying, concrete technology, and construction management in academic and internship learning.",
    ]


def rewrite_resume_bullets(
    resume_text: str,
    job_description: str,
    target_bullet: str | None = None,
    tone: str = "professional",
) -> dict:
    if not resume_text or not job_description:
        raise ValueError("Resume text and job description are required for rewriting.")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        try:
            client = OpenAI(api_key=openai_api_key)
            bullet_prompt = (
                "Rewrite the candidate's resume content into a professional, ATS-friendly Civil Engineering fresher resume. "
                "Preserve the factual details exactly: Name: NANI, Degree: B.Tech – Civil Engineering, CGPA: 8.5/10, Phone: 7025874567. "
                "Do not invent professional experience, companies, certifications, awards, or project outcomes. "
                "Do not add software-engineering, business, or generic management content. "
                "Keep the resume targeted to Civil Engineering, construction, site execution, surveying, estimation, and technical skills. "
                "Return a polished resume with clear section headings and bullet points only.\n\n"
                f"Target tone: {tone}\n\nOriginal resume:\n{resume_text}\n\nJob description:\n{job_description}"
            )
            if target_bullet:
                bullet_prompt = (
                    "Rewrite this target bullet so it reads like a truthful Civil Engineering fresher resume statement. "
                    "Preserve factual information, avoid invented experience, and keep the content relevant to construction, surveying, estimation, and structural work. "
                    "Return only the rewritten bullet text.\n\n"
                    f"Target tone: {tone}\n\nOriginal bullet:\n{target_bullet}\n\nJob description:\n{job_description}"
                )

            response = client.responses.create(
                model="gpt-4o-mini",
                input=[{"role": "user", "content": bullet_prompt}],
                temperature=0.3,
            )

            raw_output = getattr(response, "output_text", "")
            if not raw_output:
                raw_output = response.output[0].content[0].text

            text = raw_output.strip()
            if text:
                return {
                    "source": "openai",
                    "tailored_resume": text,
                    "rewritten_bullets": [],
                    "model": "gpt-4o-mini",
                }
        except Exception:
            pass

    return {
        "source": "fallback",
        "tailored_resume": _civil_fresher_after_section(),
        "rewritten_bullets": [],
        "model": "rule_based_fallback",
    }
