import re
from modules.groq_analyzer import rewrite_bullet_point

# Standard requirements for common roles
ROLE_REQUIREMENTS = {
    "Software Engineer": {
        "skills": ["Python", "Java", "C++", "Data Structures", "Algorithms", "Git", "SQL", "Unit Testing"],
        "projects": ["Build a RESTful API", "Implement a sorting algorithm visualizer", "Contribute to an open-source project"],
        "tips": ["Highlight competitive programming achievements", "Focus on clean code and SOLID principles"]
    },
    "Data Analyst": {
        "skills": ["SQL", "Python", "R", "Tableau", "PowerBI", "Excel", "Statistics", "Data Visualization"],
        "projects": ["Exploratory Data Analysis on a public dataset", "Create an automated reporting dashboard", "Perform a regression analysis project"],
        "tips": ["Emphasize data storytelling skills", "Include experience with large datasets"]
    },
    "Frontend Developer": {
        "skills": ["HTML", "CSS", "JavaScript", "React", "Vue", "Angular", "TypeScript", "Responsive Design"],
        "projects": ["Develop a responsive portfolio site", "Build a complex web app using a modern framework", "Create a reusable UI component library"],
        "tips": ["Showcase UI/UX sensibility", "Highlight performance optimization techniques"]
    },
    "Backend Developer": {
        "skills": ["Node.js", "Django", "Flask", "PostgreSQL", "MongoDB", "Redis", "Docker", "Microservices"],
        "projects": ["Architect a scalable backend system", "Implement secure authentication/authorization", "Build a real-time messaging server"],
        "tips": ["Focus on system design and database optimization", "Mention security best practices"]
    },
    "Full Stack Developer": {
        "skills": ["React", "Node.js", "Express", "Database Management", "REST APIs", "Git", "Cloud Services"],
        "projects": ["Build a full-stack SaaS application", "Develop a real-time collaboration tool", "Create an end-to-end e-commerce platform"],
        "tips": ["Highlight ability to work across the entire stack", "Mention deployment experience"]
    },
    "DevOps Engineer": {
        "skills": ["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD", "Linux", "Monitoring", "Scripting"],
        "projects": ["Setup an automated deployment pipeline", "Containerize a legacy application", "Implement Infrastructure as Code (IaC)"],
        "tips": ["Emphasize automation and reliability", "Highlight cloud-native expertize"]
    }
}

def match_resume_to_role(resume_text, role_name):
    """
    Analyzes a resume against a specific role.
    Returns a dictionary with match score, gaps, and suggestions.
    """
    if role_name not in ROLE_REQUIREMENTS:
        return None
    
    reqs = ROLE_REQUIREMENTS[role_name]
    resume_text_lower = resume_text.lower()
    
    # 1. Skill Match
    matched_skills = []
    missing_skills = []
    for skill in reqs["skills"]:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', resume_text_lower):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
            
    # Calculate score (simple percentage of skills found)
    match_score = int((len(matched_skills) / len(reqs["skills"])) * 100)
    
    # 2. Improvement Suggestions
    suggestions = reqs["tips"].copy()
    if len(missing_skills) > 0:
        suggestions.append(f"Add projects or certifications for: {', '.join(missing_skills[:3])}")
    
    # Basic content checks
    if "github.com" not in resume_text_lower and "github" not in resume_text_lower:
        suggestions.append("Add GitHub projects link to showcase your code.")
    if "leetcod" not in resume_text_lower and role_name in ["Software Engineer", "Backend Developer"]:
         suggestions.append("Include DSA problems or competitive programming links (e.g., LeetCode).")
         
    return {
        "role": role_name,
        "score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendations": suggestions,
        "projects": reqs["projects"]
    }

def get_role_list():
    return list(ROLE_REQUIREMENTS.keys())
