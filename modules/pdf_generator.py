import io
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

<<<<<<< HEAD
def generate_pdf_resume(data, template_id='classic'):
=======
def generate_pdf_resume(data, template_id='classic', ats_score=None):
>>>>>>> e68d8668670d25dd91fd1abb36f5fc1903572a6a
    """Generate a PDF resume from data dictionary with 4 professional templates."""
    name = data.get('name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
<<<<<<< HEAD
    education = data.get('education', [])
    skills = data.get('skills', '')
    projects = data.get('projects', '')
    experience = data.get('experience', '')
    certifications = data.get('certifications', [])
=======
    
    # Handle education: now a dict with 'school' and 'higher' lists
    education_data = data.get('education', {})
    education_str = ""
    if isinstance(education_data, dict):
        school_list = education_data.get('school', [])
        higher_list = education_data.get('higher', [])
        education_parts = []
        for school in school_list:
            parts = [school.get('qualification', ''), school.get('syllabus', ''), school.get('year', ''), school.get('percentage', '')]
            education_parts.append(' - '.join(filter(None, parts)))
        for higher in higher_list:
            parts = [higher.get('degree', ''), higher.get('courseName', ''), higher.get('specialization', ''), higher.get('college', ''), higher.get('graduationYear', '')]
            education_parts.append(' - '.join(filter(None, parts)))
        education_str = '\n'.join(education_parts)
    else:
        education_str = str(education_data)
    
    # Handle skills: now a list
    skills_list = data.get('skills', [])
    skills_str = ', '.join(skills_list) if isinstance(skills_list, list) else str(skills_list)
    
    # Handle projects: now a list of dicts
    projects_list = data.get('projects', [])
    projects_str = ""
    if isinstance(projects_list, list):
        proj_parts = []
        for proj in projects_list:
            title = proj.get('title', '')
            desc = proj.get('description', '')
            tech = proj.get('technologies', '')
            parts = [title, desc]
            if tech:
                parts.append(f"Technologies: {tech}")
            proj_parts.append('\n'.join(filter(None, parts)))
        projects_str = '\n\n'.join(proj_parts)
    else:
        projects_str = str(projects_list)
    
    # Handle experience: now a list of dicts
    experience_list = data.get('experience', [])
    experience_str = ""
    if isinstance(experience_list, list):
        exp_parts = []
        for exp in experience_list:
            company = exp.get('company', '')
            role = exp.get('role', '')
            duration = exp.get('duration', '')
            desc = exp.get('description', '')
            parts = [f"{role} at {company}" if role and company else role or company, duration, desc]
            exp_parts.append('\n'.join(filter(None, parts)))
        experience_str = '\n\n'.join(exp_parts)
    else:
        experience_str = str(experience_list)
    
    # Handle certifications: list of dicts
    certifications_list = data.get('certifications', [])
    certifications_str = ""
    if isinstance(certifications_list, list):
        cert_parts = []
        for cert in certifications_list:
            cert_name = cert.get('name', '')
            org = cert.get('org', '')
            year = cert.get('year', '')
            parts = [cert_name, org, year]
            cert_parts.append(' - '.join(filter(None, parts)))
        certifications_str = '\n'.join(cert_parts)
    else:
        certifications_str = str(certifications_list)
    
>>>>>>> e68d8668670d25dd91fd1abb36f5fc1903572a6a
    linkedin = data.get('linkedin', '')
    github = data.get('github', '')
    languages = data.get('languages', '')

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = inch
    y = height - margin

    # Setup Colors/Fonts for Templates
    header_color = (0, 0, 0)
    section_color = (0, 0, 0)
    font_family = 'Helvetica'
    font_bold = 'Helvetica-Bold'
    
    if template_id == 'modern':
        header_color = (0.1, 0.4, 0.7)
        section_color = (0.2, 0.5, 0.8)
    elif template_id == 'tech': # Developer
        header_color = (0.12, 0.6, 0.4)
        section_color = (0.1, 0.5, 0.3)
        font_family = 'Courier'
        font_bold = 'Courier-Bold'
    elif template_id == 'creative':
        header_color = (0.6, 0.2, 0.5)
        section_color = (0.7, 0.3, 0.6)
        font_family = 'Times-Roman'
        font_bold = 'Times-Bold'

    # Header
    c.setFillColorRGB(*header_color)
    c.setFont(font_bold, 24 if template_id in ['modern', 'creative'] else 20)
    
    if template_id == 'creative':
        # Centered creative header
        c.drawCentredString(width/2.0, y, name or 'Name')
    else:
        c.drawString(margin, y, name or 'Name')
<<<<<<< HEAD
        
=======
    
    # Add ATS Score in top right
    if ats_score is not None:
        score_text = f"ATS Score: {ats_score}/100"
        c.setFont('Helvetica', 9)
        score_width = c.stringWidth(score_text, 'Helvetica', 9)
        c.setFillColorRGB(0.1, 0.5, 0.1) if ats_score >= 70 else c.setFillColorRGB(0.8, 0.5, 0.1) if ats_score >= 50 else c.setFillColorRGB(0.8, 0.2, 0.2)
        c.drawString(width - margin - score_width, y, score_text)
    
>>>>>>> e68d8668670d25dd91fd1abb36f5fc1903572a6a
    y -= 22
    
    c.setFillColorRGB(0, 0, 0)
    # contact line
    contact = ' | '.join([p for p in [email, phone] if p])
    
    if template_id == 'creative':
        c.drawCentredString(width/2.0, y, contact)
    else:
        c.drawString(margin, y, contact)
        
    y -= 18
    if linkedin or github or languages:
        contact2 = []
        if linkedin: contact2.append(f"LinkedIn: {linkedin}")
        if github: contact2.append(f"GitHub: {github}")
        if languages: contact2.append(f"Languages: {languages}")
        c.setFont(font_family, 9)
        if template_id == 'creative':
             c.drawCentredString(width/2.0, y, ' | '.join(contact2))
        else:
             c.drawString(margin, y, ' | '.join(contact2))
        y -= 20

    def draw_section(title, text):
        nonlocal y
        # Handle: text might be a list instead of string (shouldn't happen but being safe)
        if isinstance(text, list):
            text = '\n'.join(str(t) for t in text if t)
        if not text:
            return
        c.setFillColorRGB(*section_color)
        c.setFont(font_bold, 13)
        c.drawString(margin, y, title.upper())
        y -= 6
        
        if template_id != 'creative':
            c.setLineWidth(1)
            c.setStrokeColorRGB(*section_color)
            c.line(margin, y, width - margin, y)
            
        y -= 12
        c.setFillColorRGB(0, 0, 0)
        c.setFont(font_family, 10)
        
        max_chars = 95 if font_family != 'Courier' else 80
        
        for paragraph in text.split('\n'):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            lines = textwrap.wrap(paragraph, max_chars) or ['']
            for line in lines:
                if y < margin + 40:
                    c.showPage()
                    y = height - margin
                    c.setFont(font_family, 10)
                c.drawString(margin, y, line)
                y -= 14
        y -= 10

    def draw_projects(projects_data):
        nonlocal y
        if not projects_data:
            return
            
        c.setFillColorRGB(*section_color)
        c.setFont(font_bold, 13)
        c.drawString(margin, y, "PROJECTS")
        y -= 6
        
        if template_id != 'creative':
            c.setLineWidth(1)
            c.setStrokeColorRGB(*section_color)
            c.line(margin, y, width - margin, y)
        
        y -= 12
        
        for proj in projects_data:
            title = proj.get('title', 'Untitled Project')
            role = proj.get('role', '')
            org = proj.get('org', '')
            duration = proj.get('duration', '')
            desc = proj.get('description', '')
            tech = proj.get('technologies', '')
            
            # Start position for this project
            start_y = y
            
            # Left Column (approx 35% of width)
            left_w = 2.0 * inch
            c.setFont(font_bold, 10)
            c.setFillColorRGB(0, 0, 0)
            
            # Draw Title (Bold)
            title_lines = textwrap.wrap(title, 25)
            curr_y = y
            for line in title_lines:
                c.drawString(margin, curr_y, line)
                curr_y -= 12
            
            # Draw Role/Org/Duration (Reg)
            c.setFont(font_family, 9)
            c.setFillColorRGB(0.3, 0.3, 0.3)
            if role:
                c.drawString(margin, curr_y, role)
                curr_y -= 11
            if org:
                c.drawString(margin, curr_y, org)
                curr_y -= 11
            if duration:
                c.drawString(margin, curr_y, duration)
                curr_y -= 11
            
            # Right Column (Description)
            c.setFont(font_family, 10)
            c.setFillColorRGB(0, 0, 0)
            right_x = margin + left_w + 0.2 * inch
            max_right_chars = 60 if font_family != 'Courier' else 50
            
            # Split description into bullets if it's multiple lines
            desc_y = y
            for line in desc.split('\n'):
                line = line.strip()
                if not line: continue
                if not line.startswith('\u2022') and not line.startswith('-'):
                    line = f"\u2022 {line}"
                
                wrapped_lines = textwrap.wrap(line, max_right_chars)
                for wl in wrapped_lines:
                    c.drawString(right_x, desc_y, wl)
                    desc_y -= 13
            
            # Technologies
            if tech:
                c.setFont(font_bold, 9)
                c.drawString(right_x, desc_y - 2, "Technologies:")
                c.setFont(font_family, 9)
                tech_lines = textwrap.wrap(tech, max_right_chars - 12)
                t_y = desc_y - 2
                for tl in tech_lines:
                    c.drawString(right_x + 0.7 * inch, t_y, tl)
                    t_y -= 11
                desc_y = t_y - 5
            
            # Move y to the bottom of whichever column was longer
            y = min(curr_y, desc_y) - 10
            
            # Page break check
            if y < margin + 60:
                c.showPage()
                y = height - margin
                c.setFont(font_family, 10)
        y -= 10

    def draw_experience(exp_list):
        nonlocal y
        if not exp_list:
            return
        
        c.setFillColorRGB(*section_color)
        c.setFont(font_bold, 13)
        c.drawString(margin, y, "EXPERIENCE")
        y -= 6
        
        if template_id != 'creative':
            c.setLineWidth(1)
            c.setStrokeColorRGB(*section_color)
            c.line(margin, y, width - margin, y)
        y -= 15
        
        for exp in exp_list:
            comp = exp.get('company', '')
            role = exp.get('role', '')
            dur  = exp.get('duration', '')
            desc = exp.get('description', '')
            
            if not comp and not role: continue

            # Page break check
            if y < 100:
                c.showPage()
                y = height - margin - 30
            
            c.setFillColorRGB(0, 0, 0)
            c.setFont(font_bold, 11)
            c.drawString(margin, y, comp.upper())
            
            c.setFont(font_family, 10)
            dur_width = c.stringWidth(dur, font_family, 10)
            c.drawString(width - margin - dur_width, y, dur)
            y -= 14
            
            c.setFont(font_bold, 10)
            c.drawString(margin + 5, y, role)
            y -= 12
            
            if desc:
                c.setFont(font_family, 9)
                max_chars = 95
                for line in desc.split('\n'):
                    line = line.strip()
                    if not line: continue
                    if not line.startswith('\u2022') and not line.startswith('-'):
                        line = f"\u2022 {line}"
                    
                    wrapped = textwrap.wrap(line, max_chars)
                    for wl in wrapped:
                        if y < 50:
                            c.showPage()
                            y = height - margin - 30
                            c.setFont(font_family, 9)
                        c.drawString(margin + 12, y, wl)
                        y -= 11
            y -= 10

    def draw_education(edu_data):
        nonlocal y
        if not edu_data:
            return
        
        # Handle if it's still a list (for legacy/fallback)
        if isinstance(edu_data, list):
            school_list = []
            higher_list = edu_data
        else:
            school_list = edu_data.get('school', [])
            higher_list = edu_data.get('higher', [])

        if not school_list and not higher_list:
            return

        c.setFillColorRGB(*section_color)
        c.setFont(font_bold, 13)
        c.drawString(margin, y, "EDUCATION")
        y -= 6
        
        if template_id != 'creative':
            c.setLineWidth(1)
            c.setStrokeColorRGB(*section_color)
            c.line(margin, y, width - margin, y)
        y -= 15
        
        # Draw School Education first
        for edu in school_list:
            qual = edu.get('qualification', '')
            syll = edu.get('syllabus', '')
            year = edu.get('year', '')
            perc = edu.get('percentage', '')
            
            if not qual: continue

            if y < 80:
                c.showPage()
                y = height - margin - 30
            
            c.setFillColorRGB(0, 0, 0)
            c.setFont(font_bold, 11)
            c.drawString(margin, y, f"{qual} ({syll})")
            
            c.setFont(font_family, 10)
            year_str = f"Completed: {year}" if year else ""
            y_width = c.stringWidth(year_str, font_family, 10)
            c.drawString(width - margin - y_width, y, year_str)
            y -= 14
            
            if perc:
                c.setFont(font_family, 10)
                c.drawString(margin + 5, y, f"Percentage: {perc}%")
                y -= 12
            y -= 5

        # Draw Higher Education
        for edu in higher_list:
            degree = edu.get('degree', '')
            course = edu.get('courseName', '')
            spec = edu.get('specialization', '')
            coll = edu.get('college', '')
            univ = edu.get('university', '')
            grad_year = edu.get('graduationYear', '')
            cgpa = edu.get('cgpa', '')
            duration = edu.get('duration', '')
            state = edu.get('state', '')
            district = edu.get('district', '')

            if not degree and not course and not coll: continue

            if y < 100:
                c.showPage()
                y = height - margin - 30
            
            c.setFillColorRGB(0, 0, 0)
            c.setFont(font_bold, 11)
            main_title = f"{degree} - {course}" if degree and course else (degree or course)
            c.drawString(margin, y, main_title.upper())
            
            c.setFont(font_family, 10)
            year_str = f"Graduated: {grad_year}" if grad_year else ""
            y_width = c.stringWidth(year_str, font_family, 10)
            c.drawString(width - margin - y_width, y, year_str)
            y -= 14
            
            c.setFont(font_bold, 10)
            loc_str = f" in {spec}" if spec else ""
            c.drawString(margin + 5, y, f"{coll}{loc_str}")
            y -= 12
            
            c.setFont(font_family, 9)
            univ_str = f"Affiliated to {univ}" if univ else ""
            if state or district:
                loc = f" | {district}, {state}" if district and state else f" | {district or state}"
                univ_str += loc
            c.drawString(margin + 5, y, univ_str)
            
            if cgpa or duration:
                score_str = f"CGPA: {cgpa}" if cgpa else ""
                dur_str = f"Duration: {duration} Years" if duration else ""
                info = " | ".join(filter(None, [score_str, dur_str]))
                i_width = c.stringWidth(info, font_family, 9)
                c.drawString(width - margin - i_width, y, info)
            y -= 15
        y -= 10

    # Format Certifications into a string block
    certs_text = ""
<<<<<<< HEAD
    if isinstance(certifications, list) and certifications:
        cert_blocks = []
        for cert in certifications:
=======
    if isinstance(certifications_list, list) and certifications_list:
        cert_blocks = []
        for cert in certifications_list:
>>>>>>> e68d8668670d25dd91fd1abb36f5fc1903572a6a
            cname = cert.get('name', '')
            org = cert.get('org', '')
            year = cert.get('year', '')
            link = cert.get('link', '')
            if cname:
                block = cname
                if org: block += f" \u2014 {org}"
                if year: block += f" ({year})"
                if link: block += f"\nLink: {link}"
                cert_blocks.append(block)
        certs_text = "\n\n".join(cert_blocks)
<<<<<<< HEAD
    elif isinstance(certifications, str):
        certs_text = certifications

    # Draw sections in standard order
    if isinstance(experience, list):
        draw_experience(experience)
    else:
        draw_section('Experience', experience)
    
    if isinstance(education, (list, dict)):
        draw_education(education)
    else:
        draw_section('Education', education)
    
    draw_section('Skills', skills)
    
    if isinstance(projects, list):
        draw_projects(projects)
    else:
        draw_section('Projects', projects)
    if certs_text:
        draw_section('Certifications', certs_text)
=======
    elif isinstance(certifications_list, str):
        certs_text = certifications_list

    # Draw sections in standard order
    if isinstance(experience_list, list):
        draw_experience(experience_list)
    else:
        draw_section('Experience', experience_str)
    
    if isinstance(education_data, (list, dict)):
        draw_education(education_data)
    else:
        draw_section('Education', education_str)
    
    draw_section('Skills', skills_str)
    
    if isinstance(projects_list, list):
        draw_projects(projects_list)
    else:
        draw_section('Projects', projects_str)
    if certifications_str:
        draw_section('Certifications', certifications_str)
>>>>>>> e68d8668670d25dd91fd1abb36f5fc1903572a6a

    c.save()

    buffer.seek(0)
    filename = (name.strip() or 'resume').replace(' ', '_') + '_resume.pdf'
    return buffer, filename
