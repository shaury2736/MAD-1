from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import init_db, get_db
from config import SECRET_KEY, UPLOAD_FOLDER, MAX_CONTENT_LENGTH, ALLOWED_EXTENSIONS
from utils import login_required, admin_required, company_required, student_required, allowed_file
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin': return redirect(url_for('admin_dashboard'))
        if role == 'company': return redirect(url_for('company_dashboard'))
        if role == 'student': return redirect(url_for('student_dashboard'))
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', '')
        db = get_db()

        if role == 'admin':
            admin = db.execute('SELECT * FROM admin WHERE email=?', (email,)).fetchone()
            if admin and check_password_hash(admin['password'], password):
                session['user_id'] = admin['id']
                session['role'] = 'admin'
                session['name'] = admin['name']
                return redirect(url_for('admin_dashboard'))
            flash('Invalid admin credentials.', 'danger')

        elif role == 'company':
            company = db.execute('SELECT * FROM companies WHERE email=?', (email,)).fetchone()
            if company and check_password_hash(company['password'], password):
                if company['approval_status'] == 'blacklisted':
                    flash('Your account has been blacklisted.', 'danger')
                elif company['approval_status'] != 'approved':
                    flash('Your account is pending admin approval.', 'warning')
                else:
                    session['user_id'] = company['id']
                    session['role'] = 'company'
                    session['name'] = company['company_name']
                    return redirect(url_for('company_dashboard'))
            else:
                flash('Invalid company credentials.', 'danger')

        elif role == 'student':
            student = db.execute('SELECT * FROM students WHERE email=?', (email,)).fetchone()
            if student and check_password_hash(student['password'], password):
                if student['is_blacklisted']:
                    flash('Your account has been blacklisted.', 'danger')
                else:
                    session['user_id'] = student['id']
                    session['role'] = 'student'
                    session['name'] = student['name']
                    return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid student credentials.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        roll_no = request.form.get('roll_no', '').strip()
        branch = request.form.get('branch', '').strip()
        cgpa = request.form.get('cgpa', 0)
        phone = request.form.get('phone', '').strip()

        db = get_db()
        existing = db.execute('SELECT id FROM students WHERE email=?', (email,)).fetchone()
        if existing:
            flash('Email already registered.', 'danger')
            return render_template('register_student.html')

        db.execute('''INSERT INTO students (name, email, password, roll_no, branch, cgpa, phone, is_blacklisted)
                      VALUES (?, ?, ?, ?, ?, ?, ?, 0)''',
                   (name, email, generate_password_hash(password), roll_no, branch, cgpa, phone))
        db.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register_student.html')

@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        hr_contact = request.form.get('hr_contact', '').strip()
        website = request.form.get('website', '').strip()
        industry = request.form.get('industry', '').strip()
        description = request.form.get('description', '').strip()

        db = get_db()
        existing = db.execute('SELECT id FROM companies WHERE email=?', (email,)).fetchone()
        if existing:
            flash('Email already registered.', 'danger')
            return render_template('register_company.html')

        db.execute('''INSERT INTO companies (company_name, email, password, hr_contact, website, industry, description, approval_status)
                      VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')''',
                   (company_name, email, generate_password_hash(password), hr_contact, website, industry, description))
        db.commit()
        flash('Registration submitted! Await admin approval.', 'success')
        return redirect(url_for('login'))
    return render_template('register_company.html')
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    db = get_db()
    stats = {
        'students': db.execute('SELECT COUNT(*) FROM students').fetchone()[0],
        'companies': db.execute("SELECT COUNT(*) FROM companies WHERE approval_status='approved'").fetchone()[0],
        'drives': db.execute('SELECT COUNT(*) FROM placement_drives').fetchone()[0],
        'applications': db.execute('SELECT COUNT(*) FROM applications').fetchone()[0],
        'pending_companies': db.execute("SELECT COUNT(*) FROM companies WHERE approval_status='pending'").fetchone()[0],
        'pending_drives': db.execute("SELECT COUNT(*) FROM placement_drives WHERE status='pending'").fetchone()[0],
    }
    recent_apps = db.execute('''SELECT a.id, s.name as student_name, c.company_name, pd.job_title, a.status, a.applied_date
                                FROM applications a
                                JOIN students s ON a.student_id=s.id
                                JOIN placement_drives pd ON a.drive_id=pd.id
                                JOIN companies c ON pd.company_id=c.id
                                ORDER BY a.applied_date DESC LIMIT 5''').fetchall()
    return render_template('admin/dashboard.html', stats=stats, recent_apps=recent_apps)

@app.route('/admin/companies')
@login_required
@admin_required
def admin_companies():
    db = get_db()
    q = request.args.get('q', '')
    if q:
        companies = db.execute("SELECT * FROM companies WHERE company_name LIKE ? OR id LIKE ?",
                               (f'%{q}%', f'%{q}%')).fetchall()
    else:
        companies = db.execute('SELECT * FROM companies ORDER BY id DESC').fetchall()
    return render_template('admin/companies.html', companies=companies, q=q)

@app.route('/admin/company/<int:cid>/action', methods=['POST'])
@login_required
@admin_required
def admin_company_action(cid):
    action = request.form.get('action')
    db = get_db()
    status_map = {'approve': 'approved', 'reject': 'rejected', 'blacklist': 'blacklisted', 'activate': 'approved'}
    if action in status_map:
        db.execute('UPDATE companies SET approval_status=? WHERE id=?', (status_map[action], cid))
        db.commit()
        flash(f'Company {action}d successfully.', 'success')
    return redirect(url_for('admin_companies'))

@app.route('/admin/company/<int:cid>/delete', methods=['POST'])
@login_required
@admin_required
def admin_company_delete(cid):
    db = get_db()
    db.execute('DELETE FROM companies WHERE id=?', (cid,))
    db.commit()
    flash('Company deleted.', 'success')
    return redirect(url_for('admin_companies'))

@app.route('/admin/students')
@login_required
@admin_required
def admin_students():
    db = get_db()
    q = request.args.get('q', '')
    if q:
        students = db.execute("SELECT * FROM students WHERE name LIKE ? OR id LIKE ? OR email LIKE ?",
                              (f'%{q}%', f'%{q}%', f'%{q}%')).fetchall()
    else:
        students = db.execute('SELECT * FROM students ORDER BY id DESC').fetchall()
    return render_template('admin/students.html', students=students, q=q)

@app.route('/admin/student/<int:sid>/action', methods=['POST'])
@login_required
@admin_required
def admin_student_action(sid):
    action = request.form.get('action')
    db = get_db()
    if action == 'blacklist':
        db.execute('UPDATE students SET is_blacklisted=1 WHERE id=?', (sid,))
    elif action == 'activate':
        db.execute('UPDATE students SET is_blacklisted=0 WHERE id=?', (sid,))
    db.commit()
    flash(f'Student {action}d.', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/student/<int:sid>/delete', methods=['POST'])
@login_required
@admin_required
def admin_student_delete(sid):
    db = get_db()
    db.execute('DELETE FROM students WHERE id=?', (sid,))
    db.commit()
    flash('Student deleted.', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/drives')
@login_required
@admin_required
def admin_drives():
    db = get_db()
    drives = db.execute('''SELECT pd.*, c.company_name,
                           (SELECT COUNT(*) FROM applications WHERE drive_id=pd.id) as applicant_count
                           FROM placement_drives pd
                           JOIN companies c ON pd.company_id=c.id
                           ORDER BY pd.id DESC''').fetchall()
    return render_template('admin/drives.html', drives=drives)

@app.route('/admin/drive/<int:did>/action', methods=['POST'])
@login_required
@admin_required
def admin_drive_action(did):
    action = request.form.get('action')
    db = get_db()
    status_map = {'approve': 'approved', 'reject': 'rejected'}
    if action in status_map:
        db.execute('UPDATE placement_drives SET status=? WHERE id=?', (status_map[action], did))
        db.commit()
        flash(f'Drive {action}d.', 'success')
    return redirect(url_for('admin_drives'))

@app.route('/admin/applications')
@login_required
@admin_required
def admin_applications():
    db = get_db()
    apps = db.execute('''SELECT a.*, s.name as student_name, s.roll_no, c.company_name, pd.job_title
                         FROM applications a
                         JOIN students s ON a.student_id=s.id
                         JOIN placement_drives pd ON a.drive_id=pd.id
                         JOIN companies c ON pd.company_id=c.id
                         ORDER BY a.id DESC''').fetchall()
    return render_template('admin/applications.html', apps=apps)
@app.route('/company/dashboard')
@login_required
@company_required
def company_dashboard():
    db = get_db()
    cid = session['user_id']
    company = db.execute('SELECT * FROM companies WHERE id=?', (cid,)).fetchone()
    drives = db.execute('''SELECT pd.*,
                           (SELECT COUNT(*) FROM applications WHERE drive_id=pd.id) as applicant_count
                           FROM placement_drives pd WHERE company_id=? ORDER BY id DESC''', (cid,)).fetchall()
    return render_template('company/dashboard.html', company=company, drives=drives)

@app.route('/company/drive/create', methods=['GET', 'POST'])
@login_required
@company_required
def create_drive():
    if request.method == 'POST':
        db = get_db()
        cid = session['user_id']
        db.execute('''INSERT INTO placement_drives (company_id, job_title, job_description, eligibility_criteria,
                      application_deadline, package, location, status)
                      VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')''',
                   (cid,
                    request.form.get('job_title'),
                    request.form.get('job_description'),
                    request.form.get('eligibility_criteria'),
                    request.form.get('application_deadline'),
                    request.form.get('package'),
                    request.form.get('location')))
        db.commit()
        flash('Drive created! Awaiting admin approval.', 'success')
        return redirect(url_for('company_dashboard'))
    return render_template('company/create_drive.html')

@app.route('/company/drive/<int:did>/edit', methods=['GET', 'POST'])
@login_required
@company_required
def edit_drive(did):
    db = get_db()
    drive = db.execute('SELECT * FROM placement_drives WHERE id=? AND company_id=?',
                       (did, session['user_id'])).fetchone()
    if not drive:
        flash('Drive not found.', 'danger')
        return redirect(url_for('company_dashboard'))

    if request.method == 'POST':
        db.execute('''UPDATE placement_drives SET job_title=?, job_description=?, eligibility_criteria=?,
                      application_deadline=?, package=?, location=? WHERE id=?''',
                   (request.form.get('job_title'), request.form.get('job_description'),
                    request.form.get('eligibility_criteria'), request.form.get('application_deadline'),
                    request.form.get('package'), request.form.get('location'), did))
        db.commit()
        flash('Drive updated.', 'success')
        return redirect(url_for('company_dashboard'))
    return render_template('company/edit_drive.html', drive=drive)

@app.route('/company/drive/<int:did>/delete', methods=['POST'])
@login_required
@company_required
def delete_drive(did):
    db = get_db()
    db.execute('DELETE FROM placement_drives WHERE id=? AND company_id=?', (did, session['user_id']))
    db.commit()
    flash('Drive removed.', 'success')
    return redirect(url_for('company_dashboard'))

@app.route('/company/drive/<int:did>/close', methods=['POST'])
@login_required
@company_required
def close_drive(did):
    db = get_db()
    db.execute("UPDATE placement_drives SET status='closed' WHERE id=? AND company_id=?", (did, session['user_id']))
    db.commit()
    flash('Drive closed.', 'info')
    return redirect(url_for('company_dashboard'))

@app.route('/company/drive/<int:did>/applicants')
@login_required
@company_required
def drive_applicants(did):
    db = get_db()
    drive = db.execute('SELECT * FROM placement_drives WHERE id=? AND company_id=?',
                       (did, session['user_id'])).fetchone()
    if not drive:
        flash('Drive not found.', 'danger')
        return redirect(url_for('company_dashboard'))
    applicants = db.execute('''SELECT a.*, s.name, s.email, s.roll_no, s.branch, s.cgpa, s.phone, s.resume
                               FROM applications a JOIN students s ON a.student_id=s.id
                               WHERE a.drive_id=? ORDER BY a.id DESC''', (did,)).fetchall()
    return render_template('company/applicants.html', drive=drive, applicants=applicants)

@app.route('/company/application/<int:aid>/status', methods=['POST'])
@login_required
@company_required
def update_application_status(aid):
    status = request.form.get('status')
    db = get_db()
    app_row = db.execute('''SELECT a.drive_id FROM applications a
                            JOIN placement_drives pd ON a.drive_id=pd.id
                            WHERE a.id=? AND pd.company_id=?''', (aid, session['user_id'])).fetchone()
    if app_row:
        db.execute('UPDATE applications SET status=? WHERE id=?', (status, aid))
        db.commit()
        flash(f'Application status updated to {status}.', 'success')
    did = app_row['drive_id'] if app_row else 0
    return redirect(url_for('drive_applicants', did=did))
@app.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    db = get_db()
    sid = session['user_id']
    approved_drives = db.execute('''SELECT pd.*, c.company_name,
                                    (SELECT COUNT(*) FROM applications WHERE drive_id=pd.id) as applicant_count,
                                    (SELECT id FROM applications WHERE student_id=? AND drive_id=pd.id) as applied
                                    FROM placement_drives pd
                                    JOIN companies c ON pd.company_id=c.id
                                    WHERE pd.status='approved'
                                    ORDER BY pd.id DESC''', (sid,)).fetchall()
    my_apps = db.execute('''SELECT a.*, pd.job_title, c.company_name, pd.package, pd.location
                            FROM applications a
                            JOIN placement_drives pd ON a.drive_id=pd.id
                            JOIN companies c ON pd.company_id=c.id
                            WHERE a.student_id=? ORDER BY a.id DESC''', (sid,)).fetchall()
    student = db.execute('SELECT * FROM students WHERE id=?', (sid,)).fetchone()
    return render_template('student/dashboard.html', drives=approved_drives, my_apps=my_apps, student=student)

@app.route('/student/apply/<int:did>', methods=['POST'])
@login_required
@student_required
def apply_drive(did):
    db = get_db()
    sid = session['user_id']
    existing = db.execute('SELECT id FROM applications WHERE student_id=? AND drive_id=?', (sid, did)).fetchone()
    if existing:
        flash('You have already applied for this drive.', 'warning')
        return redirect(url_for('student_dashboard'))
    drive = db.execute("SELECT * FROM placement_drives WHERE id=? AND status='approved'", (did,)).fetchone()
    if not drive:
        flash('Drive not available.', 'danger')
        return redirect(url_for('student_dashboard'))
    db.execute('INSERT INTO applications (student_id, drive_id, status, applied_date) VALUES (?, ?, ?, ?)',
               (sid, did, 'applied', datetime.now().strftime('%Y-%m-%d')))
    db.commit()
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
@student_required
def student_profile():
    db = get_db()
    sid = session['user_id']
    student = db.execute('SELECT * FROM students WHERE id=?', (sid,)).fetchone()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        branch = request.form.get('branch', '').strip()
        cgpa = request.form.get('cgpa', 0)
        bio = request.form.get('bio', '').strip()
        skills = request.form.get('skills', '').strip()
        resume_filename = student['resume']

        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename and allowed_file(file.filename):
                resume_filename = secure_filename(f"resume_{sid}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))

        db.execute('UPDATE students SET name=?, phone=?, branch=?, cgpa=?, bio=?, skills=?, resume=? WHERE id=?',
                   (name, phone, branch, cgpa, bio, skills, resume_filename, sid))
        db.commit()
        session['name'] = name
        flash('Profile updated!', 'success')
        return redirect(url_for('student_profile'))
    return render_template('student/profile.html', student=student)
@app.route('/api/stats')
@login_required
@admin_required
def api_stats():
    db = get_db()
    return jsonify({
        'students': db.execute('SELECT COUNT(*) FROM students').fetchone()[0],
        'companies': db.execute("SELECT COUNT(*) FROM companies WHERE approval_status='approved'").fetchone()[0],
        'drives': db.execute('SELECT COUNT(*) FROM placement_drives').fetchone()[0],
        'applications': db.execute('SELECT COUNT(*) FROM applications').fetchone()[0],
    })

@app.route('/api/drives')
def api_drives():
    db = get_db()
    drives = db.execute("""SELECT pd.id, pd.job_title, c.company_name, pd.package, pd.location, pd.status
                           FROM placement_drives pd JOIN companies c ON pd.company_id=c.id
                           WHERE pd.status='approved'""").fetchall()
    return jsonify([dict(d) for d in drives])

if __name__ == '__main__':
    init_db()
    os.makedirs('static/uploads', exist_ok=True)
    app.run(debug=True)
