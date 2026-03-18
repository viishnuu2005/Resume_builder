import json
import logging
import re
import os
from groq import Groq

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Groq client with the provided key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

def analyze_resume_improvement(resume_text: str, job_description: str) -> tuple[dict, int]:
    """
    Uses the Groq API (llama3-70b-8192 or similar) to perform a deep gap analysis 
    between the resume and the job description.
    
    Returns:
        (report dict, match_score int)
    """
    
    prompt = f"""
You are an expert ATS (Applicant Tracking System) and senior technical recruiter. 
Your task is to analyze the provided resume against the provided job description and output a deep gap analysis strictly in JSON format. Do not include any markdown formatting or explanatory text outside of the JSON block.

Structure your JSON EXACTLY with these keys:
{{
    "programming_languages": ["list of strings missing from resume"],
    "frameworks_and_libs": ["list of strings missing from resume"],
    "tools_and_infra": ["list of strings missing from resume"],
    "knowledge_areas": ["list of strings missing from resume"],
    "certifications": ["list of strings missing from resume"],
    "matched_skills": ["list of strings already in the resume that match the JD"],
    "resume_structure": ["list of strings (HTML allowed like <strong>) suggesting structure changes"],
    "measurable_achievements": ["list of strings (HTML allowed) suggesting how to add metrics"],
    "experience_gaps": ["list of strings (HTML allowed) describing missing experience from the JD"],
    "suggested_projects": ["list of strings suggesting 2-3 projects to build to cover gaps"],
    "jd_match_score": <integer from 0 to 100 representing the ATS match score>
}}

Job Description:
{job_description}

Resume:
{resume_text}

Provide ONLY the JSON response.
"""

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional ATS matching engine. Always output pure valid JSON without markdown wrapping."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        
        # Clean potential markdown wrap just in case
        result_text = result_text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        report = json.loads(result_text)
        
        # Extract score
        score = report.get("jd_match_score", 0)
        
        # Ensure fallback aliases for dashboard compatibility
        report["skills_to_add"] = report.get("programming_languages", []) + report.get("frameworks_and_libs", [])
        report["technologies_to_learn"] = report.get("tools_and_infra", [])
        report["knowledge_areas_required"] = report.get("knowledge_areas", [])
        report["resume_content_improvements"] = report.get("resume_structure", [])
        report["suggested_projects_to_add"] = report.get("suggested_projects", [])
        report["certifications_that_could_help"] = report.get("certifications", [])

        return report, score

    except json.JSONDecodeError as je:
        logger.error(f"Failed to decode JSON from Groq: {je}")
        # Return fallback format
        return _fallback_report(), 0
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return _fallback_report(), 0

def _fallback_report():
    return {
        "programming_languages": [],
        "frameworks_and_libs": [],
        "tools_and_infra": [],
        "knowledge_areas": [],
        "certifications": [],
        "matched_skills": [],
        "resume_structure": ["Error generating AI suggestions. Please try again."],
        "measurable_achievements": [],
        "experience_gaps": [],
        "suggested_projects": [],
        "jd_match_score": 0,
        "skills_to_add": [],
        "technologies_to_learn": [],
        "knowledge_areas_required": [],
        "resume_content_improvements": [],
        "suggested_projects_to_add": [],
        "certifications_that_could_help": []
    }
