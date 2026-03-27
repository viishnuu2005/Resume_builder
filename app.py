from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash
import io
import re
from PyPDF2 import PdfReader
from functools import wraps

# Import the new modules
from modules import resume_processor, groq_analyzer, pdf_generator, ats_analyzer, role_analyzer
from modules.database import create_user, authenticate_user, get_user_by_id, save_resume, get_user_resumes, delete_resume

app = Flask(__name__)
app.secret_key = 'resume-builder-ats-secret-key-2026'


def login_required(f):
    """Decorator to protect routes that need authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

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


@app.route('/analyze-role', methods=['GET', 'POST'])
def analyze_role():
    if request.method == 'POST':
        role_name = request.form.get('role')
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            resume_text = resume_processor.extract_text_from_pdf(file)
        else:
            resume_text = request.form.get('resume_text', '')

        if not resume_text:
            flash("Please upload a resume or provide text.")
            return redirect(url_for('analyze_role'))

        analysis = role_analyzer.match_resume_to_role(resume_text, role_name)
        if not analysis:
            flash("Invalid role selected.")
            return redirect(url_for('analyze_role'))
            
        session['role_analysis'] = analysis
        return redirect(url_for('role_dashboard'))

    roles = role_analyzer.get_role_list()
    return render_template('analyze_role.html', roles=roles)

@app.route('/role-dashboard')
def role_dashboard():
    analysis = session.get('role_analysis')
    if not analysis:
        return redirect(url_for('analyze_role'))
    return render_template('role_dashboard.html', analysis=analysis)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'GET':
        return render_template('dashboard.html')

    resume_text = request.form.get('resume_text', '').strip()

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

    # ── Validate ─────────────────────────────────────────────────────────
    if not resume_text:
        return render_template('dashboard.html',
                               error='Please upload your resume PDF or paste resume text.')

    # ── Extraction ──────────────────────────────────────────────────────
    name, email, phone = resume_processor.extract_contact_info(resume_text)
    sections           = resume_processor.split_into_sections(resume_text)

    return render_template('dashboard.html',
                           name=name,
                           email=email,
                           phone=phone,
                           education=sections.get('education', ''),
                           skills=sections.get('skills', ''),
                           projects=sections.get('projects', ''),
                           experience=sections.get('experience', ''),
                           resume_text=resume_text)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    msg = data.get('message', '').lower()
    
    response_msg = "I can help you with resume improvement tips, rewrite your sentences, or provide role-specific guidance if you've done a Role Match. Try saying 'rewrite: I led a team'."
    
    role_analysis = session.get('role_analysis')
    
    if 'rewrite' in msg or 'improve' in msg or 'bullet' in msg:

        target_text = ""
        if ':' in msg:
            target_text = msg.split(':', 1)[1].strip()
        else:
            for kw in ['rewrite', 'improve', 'bullet']:
                if kw in msg:
                    parts = msg.split(kw, 1)
                    if len(parts) > 1:
                        target_text = parts[1].strip()
                        break
        
        if target_text:
            try:
                rewritten = groq_analyzer.rewrite_bullet_point(target_text)
                response_msg = f"Here is a professional version: \"{rewritten}\""
            except Exception as e:
                response_msg = f"I tried to rewrite that, but ran into an issue: {str(e)}"
        else:
            response_msg = "Please provide the text you want me to rewrite. Example: 'rewrite: I made a website'."

    elif role_analysis and ('role' in msg or 'match' in msg or 'skill' in msg or 'missing' in msg):
        role = role_analysis.get('role')
        missing = role_analysis.get('missing_skills', [])
        score = role_analysis.get('score', 0)
        
        if 'missing' in msg or 'skill' in msg:
            if missing:
                response_msg = f"For the {role} role, you're missing: {', '.join(missing[:4])}. Adding these will boost your score!"
            else:
                response_msg = f"Your skills are a great match for a {role}! Focus on highlighting your projects now."
        elif 'match' in msg or 'score' in msg:
            response_msg = f"Your current strength for the {role} role is {score}%. Try adding some of the recommended projects to improve it."
        else:
            response_msg = f"We're currently analyzing your fit for a {role} position. Check the 'Role Match' dashboard for full details."

    elif 'resume' in msg:
        response_msg = "To optimize your resume: Add measurable achievements in your experience section and ensure you use a clean, ATS-friendly layout."

        
    return {"response": response_msg}


def _get_resume_data_from_request():
    # Extract certifications
    cert_names = request.form.getlist('cert_name[]')
    cert_orgs  = request.form.getlist('cert_org[]')
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

    skills_input = request.form.getlist('skills')
    if not skills_input and request.form.get('skills'):
        skills_input = [request.form.get('skills')]
    skills_str = ", ".join(filter(None, skills_input))

    # Extract structured experience
    exp_companies = request.form.getlist('exp_company[]')
    exp_roles     = request.form.getlist('exp_role[]')
    exp_durations = request.form.getlist('exp_duration[]')
    exp_descs     = request.form.getlist('exp_desc[]')
    
    experience_list = []
    # Support backward compatibility for single 'experience' field
    if not exp_companies and request.form.get('experience'):
        experience_list.append({
            'company': '',
            'role': '',
            'duration': '',
            'description': request.form.get('experience', '')
        })
    else:
        for i in range(len(exp_companies)):
            if exp_companies[i].strip() or (i < len(exp_roles) and exp_roles[i].strip()) or \
               (i < len(exp_durations) and exp_durations[i].strip()) or \
               (i < len(exp_descs) and exp_descs[i].strip()):
                experience_list.append({
                    'company': exp_companies[i].strip() if i < len(exp_companies) else '',
                    'role': exp_roles[i].strip() if i < len(exp_roles) else '',
                    'duration': exp_durations[i].strip() if i < len(exp_durations) else '',
                    'description': exp_descs[i].strip() if i < len(exp_descs) else ''
                })

    # Extract structured projects
    p_titles   = request.form.getlist('project_title[]')
    p_roles    = request.form.getlist('project_role[]')
    p_orgs     = request.form.getlist('project_org[]')
    p_durations = request.form.getlist('project_duration[]')
    p_descs    = request.form.getlist('project_desc[]')
    p_techs    = request.form.getlist('project_tech[]')
    
    projects_list = []
    # Support backward compatibility for single 'projects' field
    if not p_titles and request.form.get('projects'):
        projects_list.append({
            'title': '',
            'role': '',
            'org': '',
            'duration': '',
            'description': request.form.get('projects', ''),
            'technologies': ''
        })
    else:
        for i in range(len(p_titles)):
            if p_titles[i].strip():
                projects_list.append({
                    'title': p_titles[i].strip(),
                    'role': p_roles[i].strip() if i < len(p_roles) else '',
                    'org': p_orgs[i].strip() if i < len(p_orgs) else '',
                    'duration': p_durations[i].strip() if i < len(p_durations) else '',
                    'description': p_descs[i].strip() if i < len(p_descs) else '',
                    'technologies': p_techs[i].strip() if i < len(p_techs) else ''
                })

    # Extract School Education
    school_quals = request.form.getlist('school_qualification[]')
    school_syllabi = request.form.getlist('school_syllabus[]')
    school_syllabi_other = request.form.getlist('school_syllabus_other[]')
    school_years = request.form.getlist('school_year[]')
    school_percs = request.form.getlist('school_percentage[]')

    school_list = []
    for i in range(len(school_quals)):
        if school_quals[i].strip():
            syllabus = school_syllabi[i] if i < len(school_syllabi) else ''
            if syllabus == 'Other' and i < len(school_syllabi_other):
                syllabus = school_syllabi_other[i].strip()
            
            school_list.append({
                'qualification': school_quals[i].strip(),
                'syllabus': syllabus,
                'year': school_years[i].strip() if i < len(school_years) else '',
                'percentage': school_percs[i].strip() if i < len(school_percs) else ''
            })

    # Extract Higher Education
    h_degrees = request.form.getlist('higher_degree[]')
    h_courses = request.form.getlist('higher_course[]')
    h_specs = request.form.getlist('higher_specialization[]')
    h_specs_other = request.form.getlist('higher_specialization_other[]')
    h_types = request.form.getlist('higher_inst_type[]')
    h_colleges = request.form.getlist('higher_college[]')
    h_colleges_other = request.form.getlist('higher_college_other[]')
    h_univs = request.form.getlist('higher_univ[]')
    h_univs_other = request.form.getlist('higher_univ_other[]')
    h_states = request.form.getlist('higher_state[]')
    h_districts = request.form.getlist('higher_district[]')
    h_durations = request.form.getlist('higher_duration[]')
    h_years = request.form.getlist('higher_grad_year[]')
    h_cgpas = request.form.getlist('higher_cgpa[]')

    higher_list = []
    for i in range(len(h_degrees)):
        if h_degrees[i].strip() or (i < len(h_courses) and h_courses[i].strip()):
            spec = h_specs[i] if i < len(h_specs) else ''
            if spec == 'Other' and i < len(h_specs_other):
                spec = h_specs_other[i].strip()
            
            college = h_colleges[i] if i < len(h_colleges) else ''
            if college == 'Other' and i < len(h_colleges_other):
                college = h_colleges_other[i].strip()
            
            univ = h_univs[i] if i < len(h_univs) else ''
            if univ == 'Other' and i < len(h_univs_other):
                univ = h_univs_other[i].strip()

            higher_list.append({
                'degree': h_degrees[i].strip(),
                'courseName': h_courses[i].strip() if i < len(h_courses) else '',
                'specialization': spec,
                'institutionType': h_types[i].strip() if i < len(h_types) else '',
                'college': college,
                'university': univ,
                'state': h_states[i].strip() if i < len(h_states) else '',
                'district': h_districts[i].strip() if i < len(h_districts) else '',
                'duration': h_durations[i].strip() if i < len(h_durations) else '',
                'graduationYear': h_years[i].strip() if i < len(h_years) else '',
                'cgpa': h_cgpas[i].strip() if i < len(h_cgpas) else ''
            })

    education_data = {
        'school': school_list,
        'higher': higher_list
    }

    return {
        'name': request.form.get('name', ''),
        'email': request.form.get('email', ''),
        'phone': request.form.get('phone', ''),
        'linkedin': request.form.get('linkedin', ''),
        'github': request.form.get('github', ''),
        'languages': request.form.get('languages', ''),
        'education': education_data,
        'skills': request.form.getlist('skills'),
        'experience': experience_list, # Now a list of dicts
        'projects': projects_list, # Now a list of dicts
        'certifications': certifications
    }

@app.route('/download', methods=['POST'])
def download():
    """Generate a PDF resume from posted form fields and return it as a download."""
    data = _get_resume_data_from_request()
    template_id = request.form.get('template_id', 'classic')
    
    try:
        buffer, filename = pdf_generator.generate_pdf_resume(data, template_id)

        # Save resume to MongoDB if user is logged in
        if 'user_id' in session:
            save_resume(session['user_id'], data)
        
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




# ══════════════════════════════════════════════════════════════════════════════
# AUTH ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    if not name or not email or not password:
        return render_template('register.html', error='All fields are required.')
    if len(password) < 6:
        return render_template('register.html', error='Password must be at least 6 characters.')

    user = create_user(name, email, password)
    if not user:
        return render_template('register.html', error='Email already registered. Please login.')

    return render_template('login.html', success='Account created! Please login.')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    user = authenticate_user(email, password)
    if not user:
        return render_template('login.html', error='Invalid email or password.')

    session['user_id'] = user['_id']
    session['user_name'] = user['name']
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/my-resumes')
@login_required
def my_resumes():
    resumes = get_user_resumes(session['user_id'])
    return render_template('my_resumes.html',
                           resumes=resumes,
                           user_name=session.get('user_name', 'User'))


@app.route('/download-saved/<resume_id>', methods=['POST'])
@login_required
def download_saved(resume_id):
    """Re-generate and download a previously saved resume."""
    resumes = get_user_resumes(session['user_id'])
    target = None
    for r in resumes:
        if r['_id'] == resume_id:
            target = r
            break
    if not target:
        return redirect(url_for('my_resumes'))

    data = target['data']
    template_id = data.get('template_id', 'modern')
    try:
        buffer, filename = pdf_generator.generate_pdf_resume(data, template_id)
        try:
            return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
        except TypeError:
            return send_file(buffer, as_attachment=True, attachment_filename=filename, mimetype='application/pdf')
    except Exception as e:
        return f"Error generating PDF: {e}", 500


@app.route('/delete-resume/<resume_id>', methods=['POST'])
@login_required
def delete_resume_route(resume_id):
    delete_resume(resume_id, session['user_id'])
    return redirect(url_for('my_resumes'))


if __name__ == '__main__':
    app.run(debug=True)
