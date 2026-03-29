import re
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_stream):
    """Extracts raw text from a PDF stream."""
    try:
        reader = PdfReader(pdf_stream)
        extracted_text = []
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                extracted_text.append(txt)
        return '\n'.join(extracted_text)
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def extract_contact_info(text):
    """Basic extraction of email, phone, and name heuristics."""
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone_match = re.search(r"\+?\d[\d\s().-]{6,}\d", text)
    email = email_match.group(0) if email_match else ''
    phone = phone_match.group(0) if phone_match else ''

    name = ''
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        candidate = lines[0]
        if email not in candidate and (not phone or phone not in candidate) and 1 < len(candidate.split()) <= 5:
            name = candidate
            
    return name, email, phone

def split_into_sections(text):
    """Attempt to split flat text into Education, Skills, Projects, Experience sections."""
    sections = {
        "education": "",
        "skills": "",
        "projects": "",
        "experience": ""
    }
    
    current_section = None
    lines = text.split('\n')
    
    section_patterns = {
        "education": r"^(education|academic background)\b",
        "skills": r"^(skills|technical skills|technologies)\b",
        "projects": r"^(projects|personal projects)\b",
        "experience": r"^(experience|work experience|employment history)\b"
    }

    for line in lines:
        cleaned_line = line.strip().lower()
        
        # Check if line indicates a new section
        found_new = False
        for sec_name, pattern in section_patterns.items():
            if re.match(pattern, cleaned_line):
                current_section = sec_name
                found_new = True
                break
                
        if not found_new and current_section:
            sections[current_section] += line + "\n"
            
    # Clean up whitespace
    for k in sections:
        sections[k] = sections[k].strip()
        
    return sections
