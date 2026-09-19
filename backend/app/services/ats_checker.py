import re
from collections import Counter


def normalize_text(text: str) -> str:
    return re.sub(r'[^a-z0-9\s]', ' ', text.lower())


def extract_keywords(text: str) -> list[str]:
    tokens = normalize_text(text).split()
    word_counts = Counter(tokens)
    common_words = {
        'the', 'and', 'for', 'with', 'that', 'this', 'from', 'into', 'your', 'have',
        'been', 'will', 'should', 'about', 'they', 'them', 'their', 'are', 'was', 'were',
        'using', 'used', 'more', 'most', 'than', 'also', 'through', 'within', 'after', 'before'
    }
    keywords = [word for word, count in word_counts.most_common(25) if word not in common_words and count > 0]
    return keywords


def analyze_resume_match(resume_text: str, job_description: str) -> dict:
    resume_keywords = set(extract_keywords(resume_text))
    job_keywords = set(extract_keywords(job_description))

    match_keywords = sorted(job_keywords.intersection(resume_keywords))
    missing_keywords = sorted(job_keywords - resume_keywords)

    coverage = len(match_keywords) / len(job_keywords) if job_keywords else 0
    ats_score = round(coverage * 100)

    suggestions = [
        f"Add more evidence around '{keyword}' in your resume." for keyword in missing_keywords[:3]
    ] or ["Your resume aligns well with the target position. Keep it specific and measurable."]

    return {
        'ats_score': max(0, min(100, ats_score)),
        'match_percentage': max(0, min(100, round(coverage * 100))),
        'missing_keywords': missing_keywords[:8],
        'suggestions': suggestions,
    }
