import json
import logging
import re
import os
import certifi
import httpx
from groq import Groq

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Groq client with the provided key and cert bundle
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
http_client = httpx.Client(verify=certifi.where())
client = Groq(api_key=GROQ_API_KEY, http_client=http_client)

def analyze_resume_improvement(resume_text: str, job_description: str) -> tuple[dict, int]:
    """
    Uses the Groq API to perform a deep semantic gap analysis 
    between the resume and the job description.
    The match score is logically computed in Python based on the LLM's categorized outputs.
    """
    prompt = f"""
You are an expert ATS (Applicant Tracking System) and senior technical recruiter. 
Your task is to analyze the provided resume against the provided job description and output a deep gap analysis strictly in JSON format. Do not include any markdown formatting or explanatory text outside of the JSON block.
Take semantic equivalence into account. If the JD asks for 'Teamwork' and the resume says 'Strong team player', that IS a match.

Structure your JSON EXACTLY with these keys:
{{
    "programming_languages": ["list of languages required by JD but missing from resume"],
    "frameworks_and_libs": ["list of frameworks required by JD but missing from resume"],
    "tools_and_infra": ["list of tools required by JD but missing from resume"],
    "knowledge_areas": ["list of concepts/knowledge required by JD but missing from resume"],
    "certifications": ["list of certifications required by JD but missing from resume"],
    "matched_skills": ["exhaustive list of ALL skills, tools, and languages from the JD that ARE found in the resume"],
    "resume_structure": ["list of strings (HTML allowed like <strong>) suggesting structure changes"],
    "measurable_achievements": ["list of strings (HTML allowed) suggesting how to add metrics"],
    "experience_gaps": ["list of strings (HTML allowed) describing missing experience scopes"],
    "suggested_projects": ["list of strings suggesting 2-3 projects to build to cover gaps"]
}}

Job Description:
{job_description}

Resume:
{resume_text}

Provide ONLY the JSON response, no markdown blocks.
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
        
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        report = json.loads(result_text)
        
        # ── Logical Scoring in Python ──
        # Instead of hallucinating a score, we derive it from the lists provided by the LLM
        # We must use (report.get(...) or []) to defend against explicitly returned `null` from the LLM.
        
        missing_count = sum([
            len(report.get("programming_languages") or []),
            len(report.get("frameworks_and_libs") or []),
            len(report.get("tools_and_infra") or []),
            len(report.get("knowledge_areas") or []),
            len(report.get("certifications") or [])
        ])
        
        matched_count = len(report.get("matched_skills") or [])
        total_requirements = missing_count + matched_count
        
        if total_requirements > 0:
            score = int((matched_count / total_requirements) * 100)
        else:
            score = 80 # Default when no hard technical skills are found in JD
            
        report["jd_match_score"] = score
        
        # Ensure fallback aliases for dashboard compatibility
        report["skills_to_add"] = (report.get("programming_languages") or []) + (report.get("frameworks_and_libs") or [])
        report["technologies_to_learn"] = report.get("tools_and_infra") or []
        report["knowledge_areas_required"] = report.get("knowledge_areas") or []
        report["resume_content_improvements"] = report.get("resume_structure") or []
        report["suggested_projects_to_add"] = report.get("suggested_projects") or []
        report["certifications_that_could_help"] = report.get("certifications") or []

        return report, score

    except json.JSONDecodeError as je:
        logger.error(f"Failed to decode JSON from Groq: {je}")
        return _fallback_report(f"JSON parsing error from AI. Please try answering again. (details: {str(je)})"), 0
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return _fallback_report(f"Groq API Error: {str(e)}"), 0

def get_groq_response(prompt: str, temperature: float = 0.3, max_tokens: int = 500) -> str:
    """
    Generic function to get a response from Groq API for any custom prompt.
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for resume writing."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in get_groq_response: {e}")
        return f"I encountered an error: {str(e)}"

def rewrite_bullet_point(text: str) -> str:
    """
    Uses Groq AI to rewrite a simple sentence into a high-impact, professional resume bullet point.
    """
    prompt = f"""
You are an expert resume writer. Rewrite the following sentence into ONE professional resume bullet point.
- Use a strong action verb at the beginning.
- Focus on results or achievements if possible.
- Keep it concise and impactful.
- Output ONLY the rewritten bullet point, no quotes, no extra text.

Sentence: {text}
"""
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional resume writer. Respond only with the improved bullet point."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in rewrite_bullet_point: {e}")
        return text # Fallback to original text if AI fails

def _fallback_report(error_msg: str = "Error generating AI suggestions. Please try again."):
    return {
        "programming_languages": [],
        "frameworks_and_libs": [],
        "tools_and_infra": [],
        "knowledge_areas": [],
        "certifications": [],
        "matched_skills": [],
        "resume_structure": [error_msg],
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
