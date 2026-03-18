from flask import Flask, render_template, request, send_file
import io
import re
from PyPDF2 import PdfReader

# Import the new modules
from modules import resume_processor, jd_matcher, pdf_generator, ats_analyzer

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Legacy route, kept returning result.html for standard generation
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    education = request.form.get('education', '')
    skills = request.form.get('skills', '')
    projects = request.form.get('projects', '')
    linkedin = request.form.get('linkedin', '')
    github = request.form.get('github', '')
    languages = request.form.get('languages', '')

    resume_text = " ".join([name, education, skills, projects, linkedin, github, languages])

    keywords = ["Python", "Java", "SQL", "HTML", "CSS", "Flask"]

    count = 0
    for word in keywords:
        if word.lower() in resume_text.lower():
            count += 1

    score = int((count / len(keywords)) * 100) if keywords else 0

    return render_template('result.html',
                           name=name,
                           email=email,
                           phone=phone,
                           education=education,
                           skills=skills,
                           projects=projects,
                           linkedin=linkedin,
                           github=github,
                           languages=languages,
                           experience=request.form.get('experience', ''),
                           certifications=_get_resume_data_from_request().get('certifications', []),
                           score=score)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload a PDF resume and receive a standalone ATS analysis (no job description needed)."""
    if request.method == 'GET':
        return render_template('upload.html')

    uploaded = request.files.get('file')
    if not uploaded or uploaded.filename == '':
        return render_template('upload.html', error='Please choose a PDF file to upload.')

    if not uploaded.filename.lower().endswith('.pdf'):
        return render_template('upload.html', error='Only PDF files are supported.')

    try:
        resume_text = resume_processor.extract_text_from_pdf(uploaded.stream)
    except Exception as e:
        return render_template('upload.html', error=f'Error reading PDF: {e}')

    if not resume_text or not resume_text.strip():
        return render_template('upload.html', error='Could not extract text from the PDF. Make sure it is not a scanned image.')

    analysis = ats_analyzer.analyze(resume_text)
    filename = uploaded.filename.rsplit('.', 1)[0]

    return render_template('ats_result.html',
                           filename=filename,
                           analysis=analysis)


@app.route('/download-ats-report', methods=['POST'])
def download_ats_report():
    """Generate and download a plain-text ATS analysis report as a PDF."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
    from reportlab.lib.units import cm

    filename    = request.form.get('filename', 'Resume')
    score       = request.form.get('score', '0')
    grade       = request.form.get('grade', '-')
    word_count  = request.form.get('word_count', '0')
    found       = request.form.getlist('sections_found')
    missing     = request.form.getlist('sections_missing')
    suggestions_titles  = request.form.getlist('suggestion_title')
    suggestions_details = request.form.getlist('suggestion_detail')

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    primary = colors.HexColor('#0d6efd')
    dark    = colors.HexColor('#1a1a2e')

    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                 fontSize=22, textColor=dark, spaceAfter=4)
    sub_style   = ParagraphStyle('Sub',   parent=styles['Normal'],
                                 fontSize=11, textColor=colors.grey, spaceAfter=12)
    h2_style    = ParagraphStyle('H2',    parent=styles['Heading2'],
                                 fontSize=13, textColor=primary, spaceBefore=14, spaceAfter=4)
    body_style  = ParagraphStyle('Body',  parent=styles['Normal'],
                                 fontSize=10, leading=14, spaceAfter=6)
    bullet_style= ParagraphStyle('Bullet',parent=styles['Normal'],
                                 fontSize=10, leading=14, leftIndent=14, spaceAfter=3)

    story = []
    story.append(Paragraph(f"ATS Analysis Report", title_style))
    story.append(Paragraph(f"Resume: {filename}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary, spaceAfter=12))

    # Score summary table
    score_data = [
        ['ATS Score', 'Grade', 'Word Count', 'Sections Found', 'Sections Missing'],
        [f"{score}/100", grade, word_count, str(len(found)), str(len(missing))]
    ]
    t = Table(score_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 3.5*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 10),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f0f4ff'), colors.white]),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('ROUNDEDCORNERS', [4]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    # Sections
    story.append(Paragraph("Sections Detected", h2_style))
    if found:
        for s in found:
            story.append(Paragraph(f"<font color='#198754'>✔</font>  {s}", bullet_style))
    else:
        story.append(Paragraph("None detected.", body_style))

    story.append(Paragraph("Missing Sections", h2_style))
    if missing:
        for s in missing:
            story.append(Paragraph(f"<font color='#dc3545'>✘</font>  {s}", bullet_style))
    else:
        story.append(Paragraph("None — all sections present!", body_style))

    # Suggestions
    if suggestions_titles:
        story.append(Paragraph("Improvement Suggestions", h2_style))
        for i, (title, detail) in enumerate(zip(suggestions_titles, suggestions_details), 1):
            story.append(Paragraph(f"<b>{i}. {title}</b>", body_style))
            clean_detail = re.sub(r'<[^>]+>', '', detail)
            story.append(Paragraph(clean_detail, bullet_style))
            story.append(Spacer(1, 4))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#dee2e6'), spaceBefore=16))
    story.append(Paragraph("Generated by Resume Builder ATS — ATS Analysis Module", sub_style))

    doc.build(story)
    buffer.seek(0)

    report_name = f"{filename}_ATS_Report.pdf"
    try:
        return send_file(buffer, as_attachment=True, download_name=report_name, mimetype='application/pdf')
    except TypeError:
        return send_file(buffer, as_attachment=True, attachment_filename=report_name, mimetype='application/pdf')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'GET':
        return render_template('dashboard.html')

    job_description = request.form.get('job_description', '').strip()
    resume_text     = request.form.get('resume_text', '').strip()

    # ── Resume: prefer PDF upload over pasted text ──────────────────────
    resume_file = request.files.get('resume_file')
    if resume_file and resume_file.filename:
        fname = resume_file.filename.lower()
        if fname.endswith('.pdf'):
            try:
                resume_text = resume_processor.extract_text_from_pdf(resume_file.stream)
            except Exception as e:
                return render_template('dashboard.html', error=f'Error reading resume PDF: {e}')
        else:
            return render_template('dashboard.html', error='Resume must be a PDF file.')

    # ── Job Description: prefer file upload over pasted text ─────────────
    jd_file = request.files.get('jd_file')
    if jd_file and jd_file.filename:
        fname = jd_file.filename.lower()
        if fname.endswith('.pdf'):
            try:
                job_description = resume_processor.extract_text_from_pdf(jd_file.stream)
            except Exception as e:
                return render_template('dashboard.html', error=f'Error reading JD PDF: {e}')
        elif fname.endswith('.txt'):
            try:
                job_description = jd_file.read().decode('utf-8', errors='ignore')
            except Exception as e:
                return render_template('dashboard.html', error=f'Error reading JD text file: {e}')
        else:
            return render_template('dashboard.html', error='Job description file must be PDF or TXT.')

    # ── Validate ─────────────────────────────────────────────────────────
    if not job_description:
        return render_template('dashboard.html',
                               error='Please paste a job description or upload a JD file.')
    if not resume_text:
        return render_template('dashboard.html',
                               error='Please upload your resume PDF or paste resume text.')

    # ── Analyse ──────────────────────────────────────────────────────────
    report, score = jd_matcher.analyze_resume_improvement(resume_text, job_description)

    name, email, phone = resume_processor.extract_contact_info(resume_text)
    sections           = resume_processor.split_into_sections(resume_text)

    return render_template('dashboard.html',
                           report=report,
                           score=score,
                           name=name,
                           email=email,
                           phone=phone,
                           education=sections.get('education', ''),
                           skills=sections.get('skills', ''),
                           projects=sections.get('projects', ''),
                           experience=sections.get('experience', ''),
                           job_description=job_description)


def _get_resume_data_from_request():
    # Extract dynamic certifications
    cert_names = request.form.getlist('cert_name[]')
    cert_orgs = request.form.getlist('cert_org[]')
    cert_years = request.form.getlist('cert_year[]')
    cert_links = request.form.getlist('cert_link[]')
    
    certifications = []
    for i in range(len(cert_names)):
        n = cert_names[i].strip() if i < len(cert_names) else ''
        if n:
            o = cert_orgs[i].strip() if i < len(cert_orgs) else ''
            y = cert_years[i].strip() if i < len(cert_years) else ''
            l = cert_links[i].strip() if i < len(cert_links) else ''
            certifications.append({'name': n, 'org': o, 'year': y, 'link': l})

    return {
        'name': request.form.get('name', ''),
        'email': request.form.get('email', ''),
        'phone': request.form.get('phone', ''),
        'education': request.form.get('education', ''),
        'skills': request.form.get('skills', ''),
        'projects': request.form.get('projects', ''),
        'experience': request.form.get('experience', ''),
        'certifications': certifications,
        'linkedin': request.form.get('linkedin', ''),
        'github': request.form.get('github', ''),
        'languages': request.form.get('languages', '')
    }

@app.route('/download', methods=['POST'])
def download():
    """Generate a PDF resume from posted form fields and return it as a download."""
    data = _get_resume_data_from_request()
    template_id = request.form.get('template_id', 'classic')
    
    try:
        buffer, filename = pdf_generator.generate_pdf_resume(data, template_id)
        
        # Flask 2.0+ uses download_name; older versions use attachment_filename.
        try:
            return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
        except TypeError:
             # fallback for older Flask
             return send_file(buffer, as_attachment=True, attachment_filename=filename, mimetype='application/pdf')
    except Exception as e:
        return f"Error generating PDF: {e}", 500


@app.route('/preview', methods=['POST'])
def preview():
    """Generate a PDF resume and return it for inline browser viewing."""
    data = _get_resume_data_from_request()
    template_id = request.form.get('template_id', 'classic')
    
    try:
        buffer, filename = pdf_generator.generate_pdf_resume(data, template_id)
        
        try:
             # as_attachment=False makes it open in the browser tab
             return send_file(buffer, as_attachment=False, download_name=filename, mimetype='application/pdf')
        except TypeError:
             return send_file(buffer, as_attachment=False, attachment_filename=filename, mimetype='application/pdf')
    except Exception as e:
        return f"Error generating PDF preview: {e}", 500


@app.route('/match', methods=['GET', 'POST'])
def match():
    """Legacy match route to maintain backward compatibility, redirects/points to dashboard implicitly."""
    if request.method == 'GET':
        return render_template('match.html')

    job_description = request.form.get('job_description', '')
    resume_text = request.form.get('resume_text', '')

    uploaded = request.files.get('resume_file')
    if uploaded and uploaded.filename and uploaded.filename.lower().endswith('.pdf'):
        try:
            resume_text = resume_processor.extract_text_from_pdf(uploaded.stream)
        except Exception as e:
            return render_template('match.html', error=f'Error reading uploaded PDF: {e}')

    if not job_description or not job_description.strip():
        return render_template('match.html', error='Please paste a job description to analyze.')

    # Using the new smart analyzer instead of the old cosine similarity
    report, score = jd_matcher.analyze_resume_improvement(resume_text, job_description)
    
    jd_keywords = [cat for sublist in jd_matcher.TECH_CATEGORIES.values() for cat in sublist if cat in job_description.lower()]
    suggested_skills = report.get('skills_to_add', [])[:6]
    
    present = [kw for kw in jd_keywords if kw in resume_text.lower()]
    missing = [kw for kw in jd_keywords if kw not in resume_text.lower()]

    return render_template('match.html',
                           job_description=job_description,
                           jd_keywords=jd_keywords,
                           suggested_skills=suggested_skills,
                           present=present,
                           missing=missing,
                           similarity=score,
                           resume_text=resume_text)

if __name__ == '__main__':
    app.run(debug=True)
