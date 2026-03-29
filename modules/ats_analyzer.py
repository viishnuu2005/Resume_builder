"""
ATS Resume Analyzer
Scores a resume purely on ATS best practices (no job description needed).
"""

import re

# ─────────────────────────────────────────────
# Section detection patterns
# ─────────────────────────────────────────────
SECTION_PATTERNS = {
    "Education":   r"\b(education|academic background|academic qualifications|schooling|degrees?|b\.?tech|b\.?e\.?|bachelor|master|m\.?tech|m\.?s\.?)\b",
    "Experience":  r"\b(experience|work experience|employment|professional experience|internship|internships|work history)\b",
    "Skills":      r"\b(skills|technical skills|core competencies|technologies|tech stack|proficiencies|competencies)\b",
    "Projects":    r"\b(projects|personal projects|academic projects|key projects|notable projects|portfolio)\b",
    "Summary":     r"\b(summary|objective|profile|about me|professional summary|career objective)\b",
    "Certifications": r"\b(certifications?|certificates?|accreditations?|credentials?|courses?)\b",
    "Achievements":r"\b(achievements?|accomplishments?|awards?|honors?|recognitions?)\b",
}

# Weighted scores for each detected section (total = 40 pts max)
SECTION_WEIGHTS = {
    "Education":      8,
    "Experience":     10,
    "Skills":         10,
    "Projects":       6,
    "Summary":        4,
    "Certifications": 1,
    "Achievements":   1,
}

# Common ATS-valued keywords across domains
ATS_KEYWORDS = [
    "python", "java", "javascript", "sql", "html", "css", "react", "node",
    "flask", "django", "mongodb", "postgresql", "mysql", "git", "github",
    "docker", "kubernetes", "aws", "azure", "gcp", "linux", "rest", "api",
    "machine learning", "deep learning", "data analysis", "tensorflow",
    "pytorch", "pandas", "numpy", "scikit-learn", "agile", "scrum",
    "microservices", "ci/cd", "devops", "cloud", "backend", "frontend",
    "full stack", "typescript", "c++", "c#", "golang", "kotlin", "swift",
    "android", "ios", "spring", "angular", "vue", "redis", "kafka",
    "managed", "developed", "designed", "implemented", "optimized",
    "automated", "reduced", "improved", "led", "built", "created",
    "deployed", "collaborated", "delivered", "solved", "analysed"
]

# Skills sub-keywords (targeted check)
SKILLS_KEYWORDS = [
    "python", "java", "javascript", "c++", "c#", "go", "ruby", "swift",
    "kotlin", "typescript", "sql", "html", "css", "react", "angular", "vue",
    "node.js", "flask", "django", "spring", "express", "mongodb", "mysql",
    "postgresql", "oracle", "redis", "sqlite", "git", "github", "docker",
    "kubernetes", "aws", "azure", "gcp", "linux", "jenkins", "terraform",
    "hadoop", "spark", "tableau", "power bi", "excel", "jira", "figma",
    "photoshop", "tensorflow", "pytorch", "keras", "pandas", "numpy",
    "matplotlib", "scikit", "opencv", "nlp", "machine learning", "deep learning"
]


def analyze(text: str) -> dict:
    """
    Analyze a resume text and return a full ATS analysis report.

    Returns a dict with:
        score           : int  (0 – 100)
        grade           : str  (e.g. 'Good')
        sections_found  : list[str]
        sections_missing: list[str]
        suggestions     : list[dict]  {icon, title, detail}
        breakdown       : dict  {category: {score, max, pct}}
        word_count      : int
        keyword_hits    : int
        skills_hits     : int
        has_email       : bool
        has_phone       : bool
    """
    lower = text.lower()
    suggestions = []
    breakdown = {}

    # ── 1. Section Detection (40 pts) ─────────────────────
    sections_found = []
    sections_missing = []

    for sec, pattern in SECTION_PATTERNS.items():
        if re.search(pattern, lower):
            sections_found.append(sec)
        else:
            sections_missing.append(sec)

    section_score = sum(SECTION_WEIGHTS.get(s, 0) for s in sections_found)
    section_score = min(section_score, 40)
    breakdown["Sections"] = {"score": section_score, "max": 40, "pct": int(section_score / 40 * 100)}

    # Suggestions for missing core sections
    core_missing = [s for s in sections_missing if s in ("Education", "Experience", "Skills", "Projects")]
    if core_missing:
        suggestions.append({
            "icon": "fa-solid fa-list-check",
            "color": "danger",
            "title": "Add Missing Sections",
            "detail": f"Your resume is missing: <strong>{', '.join(core_missing)}</strong>. ATS systems scan for these headings — add them with clear, standard labels."
        })
    if "Summary" in sections_missing:
        suggestions.append({
            "icon": "fa-solid fa-user-pen",
            "color": "warning",
            "title": "Add a Professional Summary",
            "detail": "A 2–3 sentence professional summary at the top boosts ATS ranking and helps recruiters quickly assess your profile."
        })
    if "Certifications" in sections_missing:
        suggestions.append({
            "icon": "fa-solid fa-certificate",
            "color": "info",
            "title": "Add Certifications",
            "detail": "Listing relevant certifications (AWS, Google, Coursera, etc.) increases keyword match rates and demonstrates credibility."
        })

    # ── 2. Contact Information (10 pts) ───────────────────
    email_match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    phone_match = re.search(r"(\+?\d[\d\s().\-]{6,}\d)", text)
    has_email = email_match is not None
    has_phone = phone_match is not None

    contact_score = (5 if has_email else 0) + (5 if has_phone else 0)
    breakdown["Contact Info"] = {"score": contact_score, "max": 10, "pct": int(contact_score / 10 * 100)}

    if not has_email:
        suggestions.append({
            "icon": "fa-solid fa-envelope",
            "color": "danger",
            "title": "Email Address Missing",
            "detail": "No email address was detected. Add a professional email address — it's essential for recruiter contact and ATS parsing."
        })
    if not has_phone:
        suggestions.append({
            "icon": "fa-solid fa-phone",
            "color": "warning",
            "title": "Phone Number Missing",
            "detail": "No phone number detected. Adding a phone number makes your resume complete and parseable by most ATS systems."
        })

    # ── 3. Resume Length (10 pts) ─────────────────────────
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    if 300 <= word_count <= 800:
        length_score = 10
    elif 200 <= word_count < 300 or 800 < word_count <= 1000:
        length_score = 6
    elif 100 <= word_count < 200 or 1000 < word_count <= 1200:
        length_score = 3
    else:
        length_score = 0

    breakdown["Length"] = {"score": length_score, "max": 10, "pct": int(length_score / 10 * 100)}

    if word_count < 300:
        suggestions.append({
            "icon": "fa-solid fa-text-height",
            "color": "warning",
            "title": "Resume is Too Short",
            "detail": f"Your resume has only ~{word_count} words. ATS systems prefer resumes with 300–800 words. Expand your experience, projects, or skills sections."
        })
    elif word_count > 1000:
        suggestions.append({
            "icon": "fa-solid fa-scissors",
            "color": "info",
            "title": "Resume May Be Too Long",
            "detail": f"Your resume has ~{word_count} words. Aim for a concise 1–2 page resume (300–800 words). Trim redundant details to improve readability."
        })

    # ── 4. Keyword Density (20 pts) ───────────────────────
    keyword_hits = sum(1 for kw in ATS_KEYWORDS if kw in lower)
    kw_ratio = keyword_hits / len(ATS_KEYWORDS)

    if kw_ratio >= 0.30:
        kw_score = 20
    elif kw_ratio >= 0.20:
        kw_score = 15
    elif kw_ratio >= 0.12:
        kw_score = 10
    elif kw_ratio >= 0.06:
        kw_score = 5
    else:
        kw_score = 0

    breakdown["Keywords"] = {"score": kw_score, "max": 20, "pct": int(kw_score / 20 * 100)}

    if kw_score < 10:
        suggestions.append({
            "icon": "fa-solid fa-magnifying-glass",
            "color": "warning",
            "title": "Increase Keyword Density",
            "detail": "Use industry-standard keywords throughout your resume (e.g., technologies, tools, action verbs like 'developed', 'optimized'). ATS ranks resumes by keyword frequency."
        })

    # ── 5. Skills Keywords (20 pts) ───────────────────────
    skills_hits = sum(1 for kw in SKILLS_KEYWORDS if kw in lower)
    sk_ratio = skills_hits / len(SKILLS_KEYWORDS)

    if sk_ratio >= 0.25:
        sk_score = 20
    elif sk_ratio >= 0.15:
        sk_score = 15
    elif sk_ratio >= 0.08:
        sk_score = 10
    elif sk_ratio >= 0.04:
        sk_score = 5
    else:
        sk_score = 0

    breakdown["Skills Coverage"] = {"score": sk_score, "max": 20, "pct": int(sk_score / 20 * 100)}

    if sk_score < 10:
        suggestions.append({
            "icon": "fa-solid fa-code",
            "color": "info",
            "title": "Expand Your Skills Section",
            "detail": "List more specific technical skills (programming languages, frameworks, databases, tools). ATS systems index each skill keyword individually."
        })

    # ── Total Score ───────────────────────────────────────
    total = section_score + contact_score + length_score + kw_score + sk_score
    score = min(max(total, 0), 100)

    # Grade
    if score >= 80:
        grade = "Excellent"
    elif score >= 60:
        grade = "Good"
    elif score >= 40:
        grade = "Fair"
    else:
        grade = "Poor"

    # General best-practice suggestions always shown when score < 80
    if score < 80:
        if not re.search(r"\b(github|linkedin|portfolio|website)\b", lower):
            suggestions.append({
                "icon": "fa-brands fa-github",
                "color": "secondary",
                "title": "Add Online Profiles",
                "detail": "Include your GitHub, LinkedIn, or portfolio URL. Recruiters and ATS systems value verifiable online presence."
            })
        if not re.search(r"\b(\d+%|\d+x|increased|decreased|reduced|improved)\b", lower):
            suggestions.append({
                "icon": "fa-solid fa-chart-line",
                "color": "secondary",
                "title": "Quantify Your Achievements",
                "detail": "Add measurable results to your experience and projects (e.g., 'Reduced load time by 30%', 'Served 10K+ users'). Numbers stand out to both ATS and humans."
            })

    return {
        "score": score,
        "grade": grade,
        "sections_found": sections_found,
        "sections_missing": sections_missing,
        "suggestions": suggestions,
        "breakdown": breakdown,
        "word_count": word_count,
        "keyword_hits": keyword_hits,
        "skills_hits": skills_hits,
        "has_email": has_email,
        "has_phone": has_phone,
    }
