import re
from collections import Counter

from resume_parser import detect_resume_sections

STOP_WORDS = {
    "the", "a", "an", "and", "or", "for", "with", "from", "into", "this", "that",
    "these", "those", "their", "them", "they", "he", "she", "it", "is", "are", "was",
    "were", "be", "been", "being", "of", "on", "in", "at", "to", "as", "by", "about",
    "over", "under", "after", "before", "through", "within", "without", "more", "most",
    "some", "such", "than", "then", "also", "your", "you", "our", "us", "we", "weve"
}


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]


def _extract_contact_info(text: str) -> dict:
    phone_match = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text)
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return {
        "phone": phone_match.group(0).strip() if phone_match else "",
        "email": email_match.group(0).strip() if email_match else "",
    }


def _extract_name(resume_text: str) -> str:
    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    if not lines:
        return "Candidate"

    first_line = lines[0]
    if len(first_line.split()) <= 6 and not re.search(r"\d|@|skills|experience|education|summary|objective|project", first_line.lower()):
        return first_line

    for line in lines:
        if re.search(r"[A-Z][a-z]+", line) and not re.search(r"experience|skills|education|project|summary|objective|phone|email|degree|cgpa", line.lower()):
            return line

    return first_line


def _extract_role_title(job_description: str) -> str:
    match = re.search(r"(?:looking for|seeking|role|position|title)\s+(?:a\s+|an\s+)?([A-Za-z0-9 /&+.-]+)", job_description, flags=re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        if title:
            return title

    match = re.search(r"\b([A-Z][A-Za-z0-9+ /&.-]+)\b", job_description)
    if match:
        return match.group(1).strip()

    return "Relevant Role"


def _build_summary(resume_text: str) -> str:
    sentences = _split_sentences(resume_text)
    if not sentences:
        return "Resume summary is not available."

    summary_sentences = []
    for sentence in sentences:
        lower = sentence.lower()
        if any(token in lower for token in ["skilled", "focused", "seeking", "experience", "worked", "developed", "prepared", "assisted", "project", "summary", "objective"]):
            summary_sentences.append(sentence)
        if len(summary_sentences) >= 2:
            break

    if not summary_sentences:
        return sentences[0]

    return " ".join(summary_sentences[:2])


def _extract_education(resume_text: str) -> list[str]:
    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    education = []
    for line in lines:
        lower = line.lower()
        if re.search(r"education|degree|b\.tech|btech|b\.e|m\.tech|master|diploma|cgpa|gpa|class", lower):
            education.append(line)
    return education[:4]


def _extract_achievements(resume_text: str) -> list[str]:
    sentences = _split_sentences(resume_text)
    achievements = []
    for sentence in sentences:
        lower = sentence.lower()
        if any(word in lower for word in ["secured", "awarded", "achieved", "participated", "completed", "delivered", "winner", "ranked"]) or re.search(r"\d+\.?\d*%|\d+\+\s*years|\d+\.?\d*\s*cgpa|\d+\s*projects", lower):
            achievements.append(sentence)
    return achievements[:4]


def _extract_experience_sentences(resume_text: str, job_keywords: set[str]) -> list[str]:
    sentences = _split_sentences(resume_text)
    selected = []
    if not sentences:
        return []

    for sentence in sentences:
        lower = sentence.lower()
        if any(keyword in lower for keyword in ["experience", "worked", "developed", "managed", "designed", "led", "assisted", "prepared", "project", "internship", "role"]) or any(keyword in lower for keyword in job_keywords):
            selected.append(sentence)
        if len(selected) >= 3:
            break

    if not selected:
        return sentences[:3]

    return selected[:3]


def _normalize_job_keywords(job_description: str) -> set[str]:
    keywords = set(extract_keywords(job_description))
    return {k for k in keywords if len(k) > 2}


def generate_recruiter_view(resume_text: str, job_description: str) -> dict:
    if not resume_text or not job_description:
        raise ValueError("Resume text and job description are required.")

    resume_keywords = set(extract_keywords(resume_text))
    job_keywords = _normalize_job_keywords(job_description)
    matched_keywords = sorted(job_keywords.intersection(resume_keywords))
    missing_keywords = sorted(job_keywords.difference(resume_keywords))

    contact = _extract_contact_info(resume_text)
    candidate_name = _extract_name(resume_text)
    role_title = _extract_role_title(job_description)
    summary = _build_summary(resume_text)
    key_skills = sorted(resume_keywords.intersection(job_keywords))[:12] if resume_keywords and job_keywords else sorted(resume_keywords)[:12]
    relevant_experience = _extract_experience_sentences(resume_text, job_keywords)
    achievements = _extract_achievements(resume_text)
    education = _extract_education(resume_text)
    strengths = []
    if matched_keywords:
        strengths.extend(matched_keywords[:5])
    if relevant_experience:
        strengths.append("Relevant experience is visible")
    if achievements:
        strengths.append("Achievable achievements identified")

    attention_items = []
    if missing_keywords:
        attention_items.extend([f"Missing keyword: {keyword}" for keyword in missing_keywords[:4]])
    if not relevant_experience:
        attention_items.append("Experience section may be too brief for quick recruiter scanning.")
    if not achievements:
        attention_items.append("Achievements and measurable results are not clearly visible.")

    section_visibility = {
        "candidate_name": bool(candidate_name),
        "contact": bool(contact["phone"] or contact["email"]),
        "summary": bool(summary),
        "skills": bool(key_skills),
        "experience": bool(relevant_experience),
        "achievements": bool(achievements),
        "education": bool(education),
        "keywords": bool(matched_keywords or missing_keywords),
    }

    return {
        "candidate_name": candidate_name,
        "contact": contact,
        "summary": summary,
        "professional_title": role_title,
        "key_skills": key_skills[:12],
        "relevant_experience": relevant_experience,
        "achievements": achievements[:4],
        "education": education,
        "matched_keywords": matched_keywords[:10],
        "missing_keywords": missing_keywords[:10],
        "strengths": strengths[:6],
        "attention_items": attention_items[:6],
        "section_visibility": section_visibility,
        "scan_summary": {
            "first_impression": "Resume presents relevant skills and role alignment visible at a glance." if matched_keywords else "Resume needs clearer role-specific keyword visibility.",
            "strongest_skills": matched_keywords[:5],
            "missing_information": missing_keywords[:5],
            "experience_relevance": "Relevant experience is visible" if relevant_experience else "Experience relevance is not clearly visible",
            "keyword_visibility": "High keyword visibility" if matched_keywords else "Low keyword visibility",
            "section_completeness": "Most key sections are visible" if section_visibility["summary"] and section_visibility["skills"] and section_visibility["experience"] else "Some sections may need clearer visibility",
        },
    }


def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


def extract_keywords(text: str) -> list[str]:
    tokens = [token for token in normalize_text(text).split() if token and token not in STOP_WORDS]
    counts = Counter(tokens)
    top_terms = [term for term, _ in counts.most_common(25)]
    return top_terms


def evaluate_formatting(resume_text: str) -> list[str]:
    feedback: list[str] = []
    cleaned = resume_text.strip()
    detected_sections = detect_resume_sections(resume_text)
    normalized_sections = {section.lower() for section in detected_sections}

    if len(cleaned.split()) < 120:
        feedback.append("Resume is quite short for a competitive ATS match; add more quantified achievements and role impact.")

    if "experience" not in normalized_sections and "work experience" not in normalized_sections:
        feedback.append("Add a clear Work Experience section with role titles, employers, and dates.")

    if not re.search(r"(?:skills|core competencies|technical skills)", resume_text.lower()):
        feedback.append("Add a dedicated Skills section with relevant tools, technologies, and proficiencies.")

    if not re.search(r"(?:education|qualification)", resume_text.lower()):
        feedback.append("Include Education or Qualifications if relevant to the target role.")

    if not re.search(r"(?:\•|\*|-|\d+\.)\s+", resume_text):
        feedback.append("Use bullet points for achievements to improve readability and ATS parsing.")

    if not feedback:
        feedback.append("Formatting is generally ATS-friendly and readable.")

    return feedback


def analyze_resume(resume_text: str, job_description: str) -> dict:
    if not resume_text or not job_description:
        raise ValueError("Resume text and job description are required.")

    resume_keywords = set(extract_keywords(resume_text))
    job_keywords = set(extract_keywords(job_description))

    matched_keywords = sorted(job_keywords.intersection(resume_keywords))
    missing_keywords = sorted(job_keywords.difference(resume_keywords))

    detected_sections = detect_resume_sections(resume_text)
    formatting_feedback = evaluate_formatting(resume_text)

    keyword_coverage = len(matched_keywords) / len(job_keywords) if job_keywords else 0.0
    required_sections = {"Summary", "Experience", "Skills"}
    section_coverage = len(required_sections.intersection(set(detected_sections))) / len(required_sections)

    formatting_score = 1.0
    if len(formatting_feedback) > 2:
        formatting_score = 0.75
    if len(formatting_feedback) > 4:
        formatting_score = 0.6

    score = round((keyword_coverage * 0.7 + section_coverage * 0.2 + formatting_score * 0.1) * 100)
    score = max(0, min(100, score))

    suggestions = []
    if missing_keywords:
        suggestions.extend([f"Add keyword coverage for '{keyword}' in your resume." for keyword in missing_keywords[:4]])
    if "Experience" not in detected_sections:
        suggestions.append("Add a Work Experience section with role-specific achievements and metrics.")
    if "Skills" not in detected_sections:
        suggestions.append("Add a Skills section that mirrors the target job description keywords.")
    if not suggestions:
        suggestions.append("Your resume is already well aligned with the role. Keep emphasizing results and measurable business impact.")

    return {
        "ats_score": score,
        "matched_keywords": matched_keywords[:10],
        "missing_keywords": missing_keywords[:10],
        "detected_sections": detected_sections,
        "formatting_feedback": formatting_feedback,
        "improvement_suggestions": suggestions,
    }
