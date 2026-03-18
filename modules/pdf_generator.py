import io
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

def generate_pdf_resume(data, template_id='classic'):
    """Generate a PDF resume from data dictionary with 4 professional templates."""
    name = data.get('name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    education = data.get('education', '')
    skills = data.get('skills', '')
    projects = data.get('projects', '')
    experience = data.get('experience', '')
    certifications = data.get('certifications', [])
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
        
    y -= 22
    
    c.setFillColorRGB(0, 0, 0)
    c.setFont(font_family, 10)
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

    # Format Certifications into a string block
    certs_text = ""
    if isinstance(certifications, list) and certifications:
        cert_blocks = []
        for c in certifications:
            name = c.get('name', '')
            org = c.get('org', '')
            year = c.get('year', '')
            link = c.get('link', '')
            if name:
                block = name
                if org: block += f" \u2014 {org}"
                if year: block += f" ({year})"
                if link: block += f"\nLink: {link}"
                cert_blocks.append(block)
        certs_text = "\n\n".join(cert_blocks)
    elif isinstance(certifications, str):
        certs_text = certifications

    # Draw sections in standard order
    draw_section('Experience', experience)
    draw_section('Education', education)
    draw_section('Skills', skills)
    draw_section('Projects', projects)
    if certs_text:
        draw_section('Certifications', certs_text)

    c.showPage()
    c.save()

    buffer.seek(0)
    filename = (name.strip() or 'resume').replace(' ', '_') + '_resume.pdf'
    return buffer, filename
