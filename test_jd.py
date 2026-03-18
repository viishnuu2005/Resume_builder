import sys
sys.path.insert(0, 'c:/Users/viish/Downloads/Resume-Builder-ATS')
from modules import jd_matcher

resume = """
John Doe | johndoe@email.com | +1 234 567 8900 | github.com/johndoe

Summary
Backend developer with 3 years of experience building REST APIs.

Experience
Software Engineer - TechCorp (2021-2024)
- Developed REST APIs using Python and Flask
- Worked with PostgreSQL and Redis
- Deployed services on AWS EC2
- Used Git and GitHub for version control

Skills
Python, Flask, PostgreSQL, Redis, Git, Docker, AWS, REST APIs

Projects
- E-commerce API with Flask and PostgreSQL
- Real-time chat app using WebSockets

Education
B.Tech Computer Science, 2020
"""

jd = """
We are looking for a Senior Backend Engineer to join our platform team.

Requirements:
- 4+ years experience with Python, Go, or Java
- Strong knowledge of microservices architecture and distributed systems
- Experience with Kubernetes, Terraform, and CI/CD pipelines (GitHub Actions, Jenkins)
- Proficiency in Kafka, Elasticsearch, MongoDB
- Familiarity with Agile/Scrum methodology
- Experience leading engineering teams and mentoring junior developers
- System design skills for high-traffic production environments
- AWS or GCP certification preferred
- Knowledge of machine learning or data pipelines is a plus
"""

report, score = jd_matcher.analyze_resume_improvement(resume, jd)
print(f"\n=== JD MATCH SCORE: {score}% ===\n")
print(f"Programming Languages missing: {report['programming_languages']}")
print(f"Frameworks missing:            {report['frameworks_and_libs']}")
print(f"Tools/Infra missing:           {report['tools_and_infra']}")
print(f"Knowledge Areas:               {report['knowledge_areas']}")
print(f"Certifications:                {report['certifications']}")
print(f"Matched skills:                {report['matched_skills'][:8]}")
print(f"\nResume Structure ({len(report['resume_structure'])} tips):")
for t in report['resume_structure']: print(f"  - {t[:80]}")
print(f"\nAchievement tips ({len(report['measurable_achievements'])}):")
for t in report['measurable_achievements']: print(f"  - {t[:80]}")
print(f"\nExperience gaps ({len(report['experience_gaps'])}):")
for t in report['experience_gaps']: print(f"  - {t[:80]}")
print(f"\nSuggested projects ({len(report['suggested_projects'])}):")
for t in report['suggested_projects']: print(f"  - {t}")
