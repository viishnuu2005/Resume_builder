"""
Enhanced Job Description Matcher
Provides deep, categorized improvement suggestions when comparing a resume
against a job description — covering languages, frameworks, tools, knowledge
areas, experience gaps, structure improvements, and measurable achievements.
"""

import re
from collections import Counter

# ───────────────────────────────────────────────────────────────────────────
# Comprehensive Tech Taxonomy  (used for gap analysis)
# ───────────────────────────────────────────────────────────────────────────
TECH_CATEGORIES = {
    "languages": [
        "python", "java", "c++", "c#", "javascript", "typescript", "ruby", "go",
        "rust", "php", "swift", "kotlin", "sql", "r", "scala", "dart", "html",
        "css", "bash", "shell", "matlab", "perl", "lua", "elixir", "haskell",
        "groovy", "cobol", "fortran", "assembly", "vba", "powershell"
    ],
    "frameworks": [
        "react", "angular", "vue", "node.js", "express", "django", "flask",
        "fastapi", "spring", "spring boot", "ruby on rails", ".net", "laravel",
        "next.js", "nuxt", "svelte", "gatsby", "flutter", "electron", "remix",
        "nest.js", "strapi", "symfony", "codeigniter", "gin", "fiber", "actix",
        "pytorch", "tensorflow", "keras", "scikit-learn", "xgboost", "hugging face",
        "langchain", "openai", "pandas", "numpy", "matplotlib", "seaborn",
        "plotly", "streamlit", "gradio"
    ],
    "tools": [
        "git", "github", "gitlab", "bitbucket", "docker", "kubernetes", "jenkins",
        "aws", "gcp", "azure", "terraform", "ansible", "linux", "jira", "confluence",
        "postman", "insomnia", "figma", "webpack", "vite", "npm", "yarn", "pnpm",
        "kafka", "redis", "mongodb", "postgresql", "mysql", "sqlite", "elasticsearch",
        "rabbitmq", "celery", "airflow", "spark", "hadoop", "tableau", "power bi",
        "looker", "dbt", "snowflake", "bigquery", "redshift", "databricks",
        "grafana", "prometheus", "datadog", "new relic", "splunk", "nginx",
        "apache", "traefik", "istio", "helm", "argocd", "circleci", "github actions",
        "sonarqube", "selenium", "cypress", "jest", "pytest", "junit", "mocha"
    ],
    "knowledge": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "neural networks", "statistics", "data analysis", "data visualization",
        "predictive modeling", "big data", "agile", "scrum", "kanban",
        "system design", "api design", "restful", "graphql", "grpc",
        "microservices", "ci/cd", "devops", "cloud computing", "serverless",
        "security", "cryptography", "tdd", "bdd", "oop", "solid",
        "data structures", "algorithms", "design patterns", "distributed systems",
        "event-driven", "caching", "load balancing", "high availability",
        "observability", "sre", "fintech", "blockchain", "web3", "llm",
        "prompt engineering", "rag", "reinforcement learning", "time series",
        "recommendation systems", "a/b testing", "product analytics"
    ],
    "certifications": [
        "aws certified", "google cloud certified", "azure certified",
        "pmp", "cism", "cisa", "cissp", "ceh", "comptia", "cisco",
        "ccna", "ccnp", "ccie", "itil", "scrum master", "cka", "ckad",
        "terraform associate", "gcp professional", "databricks certified"
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "critical thinking", "time management", "collaboration",
        "adaptability", "mentoring", "presentation", "analytical"
    ]
}

# Action verbs that signal measurable impact
IMPACT_VERBS = [
    "increased", "decreased", "reduced", "improved", "optimized", "automated",
    "accelerated", "streamlined", "boosted", "delivered", "led", "managed",
    "scaled", "migrated", "refactored", "launched", "built", "designed",
    "deployed", "architected", "mentored", "trained", "saved"
]

# Patterns indicating quantified results
METRIC_PATTERNS = [
    r"\d+\s*%",           # 30%
    r"\$\s*\d+",          # $50k
    r"\d+x\b",            # 3x
    r"\d+k\b",            # 10k users
    r"\d+\s*million",     # 1 million
    r"\d+\s*billion",
    r"reduced.*\d+",
    r"increased.*\d+",
]

# Project type hints based on JD domain keywords
PROJECT_SUGGESTIONS = {
    "machine learning": [
        "End-to-end ML pipeline (data ingestion → training → serving)",
        "Sentiment analysis or text classification model",
        "Recommendation engine using collaborative filtering",
        "Time-series forecasting dashboard",
    ],
    "data": [
        "ETL pipeline with Airflow or dbt",
        "Interactive analytics dashboard (Tableau / Power BI / Streamlit)",
        "Data lake ingestion and transformation pipeline",
    ],
    "frontend": [
        "Responsive SPA with React/Vue and REST API integration",
        "Component library with Storybook documentation",
        "Progressive Web App with offline capabilities",
    ],
    "backend": [
        "RESTful API with JWT authentication and rate limiting",
        "Microservices architecture with Docker & Kubernetes",
        "Real-time notification system using WebSockets or Kafka",
    ],
    "devops": [
        "CI/CD pipeline with GitHub Actions / Jenkins",
        "Infrastructure-as-Code project using Terraform",
        "Monitoring stack: Prometheus + Grafana setup",
    ],
    "security": [
        "Penetration testing lab write-up / CTF solutions",
        "Vulnerability scanner or SIEM integration project",
        "Secure API implementation with OAuth2 / OpenID Connect",
    ],
    "mobile": [
        "Cross-platform mobile app (Flutter / React Native)",
        "Native iOS or Android app with offline sync",
    ],
}


# ───────────────────────────────────────────────────────────────────────────
# Core Analysis Function
# ───────────────────────────────────────────────────────────────────────────

def analyze_resume_improvement(resume_text: str, job_description: str) -> tuple[dict, int]:
    """
    Deep gap analysis between a resume and a job description.

    Returns:
        (report dict, match_score int 0–100)

    Report keys:
        programming_languages   – languages in JD missing from resume
        frameworks_and_libs     – frameworks/libraries in JD missing from resume
        tools_and_infra         – tools/platforms in JD missing from resume
        knowledge_areas         – concept areas in JD missing from resume
        resume_structure        – structure/content improvement suggestions
        measurable_achievements – tips on adding metrics
        experience_gaps         – missing experience types
        suggested_projects      – project ideas relevant to the JD domain
        certifications          – useful certifications based on JD
        matched_skills          – keywords already present (positive signal)
        jd_match_score          – same as returned score
    """
    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()

    # ── Build term sets ────────────────────────────────────────────────────
    jd_terms = set(re.findall(r"\b[a-z0-9#+.\-]{2,}\b", jd_lower))
    resume_terms = set(re.findall(r"\b[a-z0-9#+.\-]{2,}\b", resume_lower))

    # also pick up multi-word phrases
    for cat_list in TECH_CATEGORIES.values():
        for term in cat_list:
            if term in jd_lower:
                jd_terms.add(term)
            if term in resume_lower:
                resume_terms.add(term)

    missing_terms = jd_terms - resume_terms

    # ── 1. Categorise missing terms ────────────────────────────────────────
    prog_langs   = sorted({t.upper() if len(t) <= 3 else t.title()
                           for t in missing_terms if t in TECH_CATEGORIES["languages"]})
    frameworks   = sorted({t.title() for t in missing_terms if t in TECH_CATEGORIES["frameworks"]})
    tools        = sorted({t.title() for t in missing_terms if t in TECH_CATEGORIES["tools"]})
    knowledge    = sorted({t.title() for t in missing_terms if t in TECH_CATEGORIES["knowledge"]})
    certs        = sorted({t.title() for t in missing_terms if t in TECH_CATEGORIES["certifications"]})

    # Already-matched (positive signal)
    matched = sorted({t.title() for t in (jd_terms & resume_terms)
                      if any(t in cat for cat in TECH_CATEGORIES.values())})

    # ── 2. Resume Structure Improvements ──────────────────────────────────
    structure_tips = []

    core_sections = {
        "education":   r"\b(education|academic|degree|bachelor|master|b\.tech|m\.tech)\b",
        "experience":  r"\b(experience|work experience|employment|internship)\b",
        "skills":      r"\b(skills|technical skills|competencies|technologies)\b",
        "projects":    r"\b(projects|portfolio|personal projects)\b",
        "summary":     r"\b(summary|objective|profile|about me)\b",
    }
    missing_secs = [sec.capitalize() for sec, pat in core_sections.items()
                    if not re.search(pat, resume_lower)]
    if missing_secs:
        structure_tips.append(
            f"Add clearly labelled sections for: <strong>{', '.join(missing_secs)}</strong>. "
            "ATS parsers rely on these headings to correctly index your data."
        )

    if not re.search(r"\b(summary|objective|profile|about me)\b", resume_lower):
        structure_tips.append(
            "Add a 2–3 sentence <strong>Professional Summary</strong> at the top "
            "that mirrors key terms from the job description — this is the first thing ATS and recruiters read."
        )

    if not re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", resume_text):
        structure_tips.append("Your <strong>email address</strong> is missing or not parseable — ensure it appears in plain text near the top.")

    if not re.search(r"\+?\d[\d\s().\-]{6,}\d", resume_text):
        structure_tips.append("No <strong>phone number</strong> detected. Add one in the contact section.")

    if not re.search(r"\b(github|linkedin|portfolio|website)\b", resume_lower):
        structure_tips.append(
            "Include your <strong>GitHub / LinkedIn / Portfolio</strong> URLs. "
            "For technical roles these are often checked by recruiters before interviews."
        )

    word_count = len(re.findall(r"\b\w+\b", resume_text))
    if word_count < 300:
        structure_tips.append(
            f"Your resume is very short (~{word_count} words). Aim for 400–700 words "
            "to give ATS and reviewers enough signal."
        )
    elif word_count > 1000:
        structure_tips.append(
            f"Your resume is long (~{word_count} words). Try to keep it to 1–2 pages "
            "(~400–700 words) — recruiters spend only 6–10 seconds on first pass."
        )

    # ── 3. Measurable Achievements ────────────────────────────────────────
    achievement_tips = []
    has_metrics = any(re.search(p, resume_lower) for p in METRIC_PATTERNS)
    has_impact_verbs = sum(1 for v in IMPACT_VERBS if v in resume_lower)

    if not has_metrics:
        achievement_tips.append(
            "No quantified results detected. Add <strong>numbers and percentages</strong> "
            "to every bullet point where possible — e.g., "
            "<em>'Reduced API latency by 35%'</em>, <em>'Onboarded 10k+ users'</em>."
        )
    if has_impact_verbs < 3:
        achievement_tips.append(
            "Use more <strong>strong action verbs</strong> to open each bullet: "
            "<em>Architected, Optimized, Automated, Scaled, Migrated, Delivered</em>, etc. "
            "These improve both ATS ranking and recruiter impression."
        )
    if not re.search(r"\b(award|recognition|honor|top|best|winner|finalist)\b", resume_lower):
        achievement_tips.append(
            "Consider adding an <strong>Achievements or Awards</strong> section "
            "if you have relevant honours, hackathon wins, or recognitions."
        )

    # ── 4. Experience Gaps (based on JD signals) ──────────────────────────
    experience_gaps = []

    if re.search(r"\b(team lead|lead|senior|manager|principal)\b", jd_lower):
        if not re.search(r"\b(led|managed|mentored|supervised|directed|owned)\b", resume_lower):
            experience_gaps.append(
                "The JD requires <strong>leadership experience</strong>. Add examples of leading "
                "teams, mentoring junior engineers, or owning end-to-end features."
            )

    if re.search(r"\b(production|large.scale|high.traffic|distributed)\b", jd_lower):
        if not re.search(r"\b(production|scale|deployed|millions|thousands|users)\b", resume_lower):
            experience_gaps.append(
                "The JD emphasises <strong>production / large-scale systems</strong>. "
                "Highlight any experience with systems serving real users, handling high traffic, "
                "or deployed in production environments."
            )

    if re.search(r"\b(client|customer|stakeholder|business)\b", jd_lower):
        if not re.search(r"\b(client|customer|stakeholder|presentation|communicated)\b", resume_lower):
            experience_gaps.append(
                "The JD involves <strong>client or stakeholder interaction</strong>. "
                "Mention any experience gathering requirements, presenting to clients, "
                "or translating business needs into technical solutions."
            )

    if re.search(r"\b(agile|scrum|kanban|sprint)\b", jd_lower):
        if not re.search(r"\b(agile|scrum|kanban|sprint|stand.?up)\b", resume_lower):
            experience_gaps.append(
                "The role uses <strong>Agile / Scrum methodology</strong>. "
                "Mention your experience working in sprint cycles, stand-ups, retrospectives, "
                "or using tools like Jira."
            )

    if re.search(r"\b(ci/cd|devops|pipeline|deploy)\b", jd_lower):
        if not re.search(r"\b(ci/cd|pipeline|deploy|jenkins|github actions|circleci)\b", resume_lower):
            experience_gaps.append(
                "The JD expects <strong>CI/CD experience</strong>. "
                "Add any pipeline setup, deployment automation, or DevOps work you've done."
            )

    # ── 5. Suggested Projects ─────────────────────────────────────────────
    suggested_projects = []
    # Detect domain from JD
    for domain, suggestions in PROJECT_SUGGESTIONS.items():
        if re.search(rf"\b{re.escape(domain)}\b", jd_lower):
            suggested_projects.extend(suggestions[:2])  # top 2 per domain

    # De-dup and cap at 5
    seen = set()
    deduped = []
    for p in suggested_projects:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    suggested_projects = deduped[:5]

    # Fallback – generic project if no domain matched
    if not suggested_projects:
        suggested_projects = [
            "Build an end-to-end project showcasing the primary technologies listed in the JD",
            "Create a GitHub repo demonstrating system design, clean code, and documentation",
        ]

    # ── 6. Match Score ─────────────────────────────────────────────────────
    jd_tracked = set()
    for cat_list in TECH_CATEGORIES.values():
        for term in cat_list:
            if term in jd_lower:
                jd_tracked.add(term)

    matched_tracked = {t for t in jd_tracked if t in resume_lower}
    score = int(len(matched_tracked) / len(jd_tracked) * 100) if jd_tracked else 0
    score = min(score, 100)

    # Also factor in structure: add 2 pts per core section present (up to 10)
    present_secs = len(core_sections) - len(missing_secs)
    score = min(score + present_secs * 2, 100)

    report = {
        "programming_languages":    prog_langs,
        "frameworks_and_libs":      frameworks,
        "tools_and_infra":          tools,
        "knowledge_areas":          knowledge,
        "certifications":           certs,
        "matched_skills":           matched[:20],   # cap display
        "resume_structure":         structure_tips,
        "measurable_achievements":  achievement_tips,
        "experience_gaps":          experience_gaps,
        "suggested_projects":       suggested_projects,
        "jd_match_score":           score,
        # Legacy keys kept for backward compat with dashboard.html
        "skills_to_add":            prog_langs + frameworks,
        "technologies_to_learn":    tools,
        "knowledge_areas_required": knowledge,
        "resume_content_improvements": structure_tips,
        "suggested_projects_to_add":   suggested_projects,
        "certifications_that_could_help": certs,
    }

    return report, score
