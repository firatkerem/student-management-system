from flask import render_template, request, redirect, url_for, flash, abort, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User, Course, Enrollment, Grade, Note, Announcement, PDFDocument
from functools import wraps
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'teacher':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def init_routes(app):
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                login_user(user)
                flash('Başarıyla giriş yaptınız!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Geçersiz email veya şifre!', 'error')
        
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')
            
            if User.query.filter_by(email=email).first():
                flash('Bu email adresi zaten kullanılıyor!', 'error')
                return render_template('register.html')
            
            user = User(name=name, email=email, role=role)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Başarıyla çıkış yaptınız!', 'success')
        return redirect(url_for('login'))

    @app.route('/student/dashboard')
    @login_required
    @student_required
    def student_dashboard():
        enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
        grades = Grade.query.filter_by(student_id=current_user.id).all()
        
        return render_template('student/dashboard.html', enrollments=enrollments, grades=grades)

    @app.route('/teacher/dashboard')
    @login_required
    @teacher_required
    def teacher_dashboard():
        return render_template('teacher/dashboard.html')

    @app.route('/teacher/students')
    @login_required
    @teacher_required
    def manage_students():
        students = User.query.filter_by(role='student').all()
        return render_template('teacher/students.html', students=students)

    @app.route('/teacher/students/add', methods=['GET', 'POST'])
    @login_required
    @teacher_required
    def add_student():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if User.query.filter_by(email=email).first():
                flash('Bu email adresi zaten kullanılıyor!', 'error')
                return render_template('teacher/add_student.html')
            
            user = User(name=name, email=email, role='student')
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Öğrenci başarıyla eklendi!', 'success')
            return redirect(url_for('manage_students'))
        
        return render_template('teacher/add_student.html')

    @app.route('/teacher/students/delete/<int:student_id>', methods=['POST'])
    @login_required
    @teacher_required
    def delete_student(student_id):
        student = User.query.get_or_404(student_id)
        if student.role != 'student':
            flash('Sadece öğrenci silebilirsiniz!', 'error')
            return redirect(url_for('manage_students'))
        
        try:
            # Önce ilişkili kayıtları sil
            # Notları sil
            Note.query.filter_by(user_id=student_id).delete()
            
            # Notları sil
            Grade.query.filter_by(student_id=student_id).delete()
            
            # Kurs kayıtlarını sil
            Enrollment.query.filter_by(student_id=student_id).delete()
            
            # Son olarak öğrenciyi sil
            db.session.delete(student)
            db.session.commit()
            
            flash('Öğrenci ve tüm ilişkili kayıtları başarıyla silindi!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Öğrenci silinirken hata oluştu: {str(e)}', 'error')
            
        return redirect(url_for('manage_students'))

    @app.route('/teacher/courses')
    @login_required
    @teacher_required
    def manage_courses():
        courses = Course.query.all()
        return render_template('teacher/courses.html', courses=courses)

    @app.route('/teacher/courses/add', methods=['GET', 'POST'])
    @login_required
    @teacher_required
    def add_course():
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            
            course = Course(name=name, description=description, teacher_id=current_user.id)
            db.session.add(course)
            db.session.commit()
            
            flash('Kurs başarıyla eklendi!', 'success')
            return redirect(url_for('manage_courses'))
        
        return render_template('teacher/add_course.html')

    @app.route('/teacher/courses/delete/<int:course_id>', methods=['POST'])
    @login_required
    @teacher_required
    def delete_course(course_id):
        course = Course.query.get_or_404(course_id)
        if course.teacher_id != current_user.id:
            flash('Sadece kendi kurslarınızı silebilirsiniz!', 'error')
            return redirect(url_for('manage_courses'))
        
        db.session.delete(course)
        db.session.commit()
        flash('Kurs başarıyla silindi!', 'success')
        return redirect(url_for('manage_courses'))

    @app.route('/teacher/enrollments')
    @login_required
    @teacher_required
    def manage_enrollments():
        enrollments = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id).all()
        students = User.query.filter_by(role='student').all()
        courses = Course.query.filter_by(teacher_id=current_user.id).all()
        return render_template('teacher/enrollments.html', enrollments=enrollments, students=students, courses=courses)

    @app.route('/teacher/enrollments/add', methods=['GET', 'POST'])
    @login_required
    @teacher_required
    def add_enrollment():
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            course_id = request.form.get('course_id')
            
            existing_enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
            if existing_enrollment:
                flash('Bu öğrenci zaten bu kursa kayıtlı!', 'error')
                return render_template('teacher/add_enrollment.html', 
                                     students=User.query.filter_by(role='student').all(),
                                     courses=Course.query.filter_by(teacher_id=current_user.id).all())
            
            enrollment = Enrollment(student_id=student_id, course_id=course_id)
            db.session.add(enrollment)
            db.session.commit()
            
            flash('Kayıt başarıyla eklendi!', 'success')
            return redirect(url_for('manage_enrollments'))
        
        students = User.query.filter_by(role='student').all()
        courses = Course.query.filter_by(teacher_id=current_user.id).all()
        return render_template('teacher/add_enrollment.html', students=students, courses=courses)

    @app.route('/teacher/enrollments/delete/<int:enrollment_id>', methods=['POST'])
    @login_required
    @teacher_required
    def delete_enrollment(enrollment_id):
        enrollment = Enrollment.query.get_or_404(enrollment_id)
        course = Course.query.get(enrollment.course_id)
        
        if course.teacher_id != current_user.id:
            flash('Sadece kendi kurslarınızın kayıtlarını silebilirsiniz!', 'error')
            return redirect(url_for('manage_enrollments'))
        
        db.session.delete(enrollment)
        db.session.commit()
        flash('Kayıt başarıyla silindi!', 'success')
        return redirect(url_for('manage_enrollments'))

    @app.route('/teacher/grades')
    @login_required
    @teacher_required
    def manage_grades():
        grades = Grade.query.join(Course).filter(Course.teacher_id == current_user.id).all()
        return render_template('teacher/grades.html', grades=grades)

    @app.route('/teacher/grades/add', methods=['GET', 'POST'])
    @login_required
    @teacher_required
    def add_grade():
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            course_id = request.form.get('course_id')
            note = request.form.get('note')
            
            enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
            if not enrollment:
                flash('Bu öğrenci bu kursa kayıtlı değil!', 'error')
                return render_template('teacher/add_grade.html', 
                                     students=User.query.filter_by(role='student').all(),
                                     courses=Course.query.filter_by(teacher_id=current_user.id).all())
            
            existing_grade = Grade.query.filter_by(student_id=student_id, course_id=course_id).first()
            if existing_grade:
                existing_grade.note = float(note)
            else:
                grade = Grade(student_id=student_id, course_id=course_id, note=float(note))
                db.session.add(grade)
            
            db.session.commit()
            flash('Not başarıyla eklendi!', 'success')
            return redirect(url_for('manage_grades'))
        
        students = User.query.filter_by(role='student').all()
        courses = Course.query.filter_by(teacher_id=current_user.id).all()
        return render_template('teacher/add_grade.html', students=students, courses=courses)

    @app.route('/teacher/grades/delete/<int:grade_id>', methods=['POST'])
    @login_required
    @teacher_required
    def delete_grade(grade_id):
        grade = Grade.query.get_or_404(grade_id)
        course = Course.query.get(grade.course_id)
        
        if course.teacher_id != current_user.id:
            flash('Sadece kendi kurslarınızın notlarını silebilirsiniz!', 'error')
            return redirect(url_for('manage_grades'))
        
        db.session.delete(grade)
        db.session.commit()
        flash('Not başarıyla silindi!', 'success')
        return redirect(url_for('manage_grades'))

    @app.route('/student/pdf')
    @login_required
    @student_required
    def student_pdf():
        enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
        grades = Grade.query.filter_by(student_id=current_user.id).all()
        return render_template('student/pdf.html', enrollments=enrollments, grades=grades)

    @app.route('/teacher/pdf')
    @login_required
    @teacher_required
    def teacher_pdf():
        courses = Course.query.filter_by(teacher_id=current_user.id).all()
        students = User.query.filter_by(role='student').all()
        return render_template('teacher/pdf.html', courses=courses, students=students)

    @app.route('/student/pdf/download')
    @login_required
    @student_required
    def download_student_pdf():
        enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
        grades = Grade.query.filter_by(student_id=current_user.id).all()
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph("Student Course Report", title_style))
        story.append(Spacer(1, 20))
        
        student_style = ParagraphStyle(
            'StudentInfo',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_LEFT
        )
        story.append(Paragraph(f"Student: {current_user.name}", student_style))
        story.append(Paragraph(f"Email: {current_user.email}", styles['Normal']))
        story.append(Paragraph(f"Report Date: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        if enrollments:
            story.append(Paragraph("Enrolled Courses", student_style))
            story.append(Spacer(1, 10))
            
            for enrollment in enrollments:
                course = enrollment.course
                story.append(Paragraph(f"• {course.name}", styles['Normal']))
                story.append(Paragraph(f"  Description: {course.description or 'No description'}", styles['Normal']))
                story.append(Paragraph(f"  Teacher: {course.teacher.name}", styles['Normal']))
                story.append(Paragraph(f"  Enrollment Date: {enrollment.enrolled_at.strftime('%d.%m.%Y')}", styles['Normal']))
                story.append(Spacer(1, 5))
        else:
            story.append(Paragraph("No enrolled courses found.", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        if grades:
            story.append(Paragraph("Grades", student_style))
            story.append(Spacer(1, 10))
            
            for grade in grades:
                course = grade.course
                story.append(Paragraph(f"• {course.name}: {grade.note}/100", styles['Normal']))
                
                if grade.note >= 70:
                    status = "Passed"
                elif grade.note >= 50:
                    status = "Average"
                else:
                    status = "Failed"
                
                story.append(Paragraph(f"  Status: {status}", styles['Normal']))
                story.append(Paragraph(f"  Date: {grade.created_at.strftime('%d.%m.%Y')}", styles['Normal']))
                story.append(Spacer(1, 5))
        else:
            story.append(Paragraph("No grades available yet.", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Summary", student_style))
        story.append(Paragraph(f"Total Enrolled Courses: {len(enrollments)}", styles['Normal']))
        story.append(Paragraph(f"Total Grades: {len(grades)}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{current_user.name}_course_report.pdf",
            mimetype='application/pdf'
        )

    @app.route('/teacher/pdf/course/<int:course_id>/download')
    @login_required
    @teacher_required
    def download_course_pdf(course_id):
        course = Course.query.get_or_404(course_id)
        
        if course.teacher_id != current_user.id:
            abort(403)
        
        enrollments = Enrollment.query.filter_by(course_id=course_id).all()
        grades = Grade.query.filter_by(course_id=course_id).all()
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"Course Report: {course.name}", title_style))
        story.append(Spacer(1, 20))
        
        course_style = ParagraphStyle(
            'CourseInfo',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_LEFT
        )
        story.append(Paragraph("Course Information", course_style))
        story.append(Paragraph(f"Course Name: {course.name}", styles['Normal']))
        story.append(Paragraph(f"Description: {course.description or 'No description'}", styles['Normal']))
        story.append(Paragraph(f"Teacher: {course.teacher.name}", styles['Normal']))
        story.append(Paragraph(f"Report Date: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Enrolled Students", course_style))
        story.append(Spacer(1, 10))
        
        if enrollments:
            for enrollment in enrollments:
                student = enrollment.student
                story.append(Paragraph(f"• {student.name} ({student.email})", styles['Normal']))
                story.append(Paragraph(f"  Enrollment Date: {enrollment.enrolled_at.strftime('%d.%m.%Y')}", styles['Normal']))
                story.append(Spacer(1, 5))
        else:
            story.append(Paragraph("No students enrolled in this course.", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Grades", course_style))
        story.append(Spacer(1, 10))
        
        if grades:
            for grade in grades:
                student = grade.student
                story.append(Paragraph(f"• {student.name}: {grade.note}/100", styles['Normal']))
                
                if grade.note >= 70:
                    status = "Passed"
                elif grade.note >= 50:
                    status = "Average"
                else:
                    status = "Failed"
                
                story.append(Paragraph(f"  Status: {status}", styles['Normal']))
                story.append(Paragraph(f"  Date: {grade.created_at.strftime('%d.%m.%Y')}", styles['Normal']))
                story.append(Spacer(1, 5))
        else:
            story.append(Paragraph("No grades available for this course.", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Summary", course_style))
        story.append(Paragraph(f"Total Enrolled Students: {len(enrollments)}", styles['Normal']))
        story.append(Paragraph(f"Total Grades: {len(grades)}", styles['Normal']))
        
        if grades:
            avg_grade = sum(grade.note for grade in grades) / len(grades)
            story.append(Paragraph(f"Average Grade: {avg_grade:.2f}/100", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{course.name}_course_report.pdf",
            mimetype='application/pdf'
        )

    @app.route('/teacher/pdf/student/<int:student_id>/download')
    @login_required
    @teacher_required
    def download_student_pdf_teacher(student_id):
        student = User.query.get_or_404(student_id)
        
        teacher_courses = Course.query.filter_by(teacher_id=current_user.id).all()
        course_ids = [course.id for course in teacher_courses]
        
        enrollments = Enrollment.query.filter(
            Enrollment.student_id == student_id,
            Enrollment.course_id.in_(course_ids)
        ).all()
        
        grades = Grade.query.filter(
            Grade.student_id == student_id,
            Grade.course_id.in_(course_ids)
        ).all()
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"Student Report: {student.name}", title_style))
        story.append(Spacer(1, 20))
        
        student_style = ParagraphStyle(
            'StudentInfo',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_LEFT
        )
        story.append(Paragraph("Student Information", student_style))
        story.append(Paragraph(f"Student Name: {student.name}", styles['Normal']))
        story.append(Paragraph(f"Email: {student.email}", styles['Normal']))
        story.append(Paragraph(f"Report Date: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        if enrollments:
            story.append(Paragraph("Enrolled Courses", student_style))
            story.append(Spacer(1, 10))
            
            for enrollment in enrollments:
                course = enrollment.course
                story.append(Paragraph(f"• {course.name}", styles['Normal']))
                story.append(Paragraph(f"  Description: {course.description or 'No description'}", styles['Normal']))
                story.append(Paragraph(f"  Enrollment Date: {enrollment.enrolled_at.strftime('%d.%m.%Y')}", styles['Normal']))
                story.append(Spacer(1, 5))
        else:
            story.append(Paragraph("No enrolled courses found.", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        if grades:
            story.append(Paragraph("Grades", student_style))
            story.append(Spacer(1, 10))
            
            for grade in grades:
                course = grade.course
                story.append(Paragraph(f"• {course.name}: {grade.note}/100", styles['Normal']))
                
                if grade.note >= 70:
                    status = "Passed"
                elif grade.note >= 50:
                    status = "Average"
                else:
                    status = "Failed"
                
                story.append(Paragraph(f"  Status: {status}", styles['Normal']))
                story.append(Paragraph(f"  Date: {grade.created_at.strftime('%d.%m.%Y')}", styles['Normal']))
                story.append(Spacer(1, 5))
        else:
            story.append(Paragraph("No grades available yet.", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Summary", student_style))
        story.append(Paragraph(f"Total Enrolled Courses: {len(enrollments)}", styles['Normal']))
        story.append(Paragraph(f"Total Grades: {len(grades)}", styles['Normal']))
        
        if grades:
            avg_grade = sum(grade.note for grade in grades) / len(grades)
            story.append(Paragraph(f"Average Grade: {avg_grade:.2f}/100", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{student.name}_student_report.pdf",
            mimetype='application/pdf'
        )

    @app.route('/teacher/pdf/general/download')
    @login_required
    @teacher_required
    def download_general_pdf():
        courses = Course.query.filter_by(teacher_id=current_user.id).all()
        
        all_enrollments = []
        all_grades = []
        
        for course in courses:
            enrollments = Enrollment.query.filter_by(course_id=course.id).all()
            grades = Grade.query.filter_by(course_id=course.id).all()
            all_enrollments.extend(enrollments)
            all_grades.extend(grades)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"General Report: {current_user.name}", title_style))
        story.append(Spacer(1, 20))
        
        teacher_style = ParagraphStyle(
            'TeacherInfo',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_LEFT
        )
        story.append(Paragraph("Teacher Information", teacher_style))
        story.append(Paragraph(f"Teacher Name: {current_user.name}", styles['Normal']))
        story.append(Paragraph(f"Email: {current_user.email}", styles['Normal']))
        story.append(Paragraph(f"Report Date: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Courses", teacher_style))
        story.append(Spacer(1, 10))
        
        if courses:
            for course in courses:
                course_enrollments = [e for e in all_enrollments if e.course_id == course.id]
                course_grades = [g for g in all_grades if g.course_id == course.id]
                
                story.append(Paragraph(f"• {course.name}", styles['Normal']))
                story.append(Paragraph(f"  Description: {course.description or 'No description'}", styles['Normal']))
                story.append(Paragraph(f"  Enrolled Students: {len(course_enrollments)}", styles['Normal']))
                story.append(Paragraph(f"  Total Grades: {len(course_grades)}", styles['Normal']))
                
                if course_grades:
                    avg_grade = sum(grade.note for grade in course_grades) / len(course_grades)
                    story.append(Paragraph(f"  Average Grade: {avg_grade:.2f}/100", styles['Normal']))
                
                story.append(Spacer(1, 5))
        else:
            story.append(Paragraph("No courses found.", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("General Statistics", teacher_style))
        story.append(Paragraph(f"Total Courses: {len(courses)}", styles['Normal']))
        story.append(Paragraph(f"Total Enrollments: {len(all_enrollments)}", styles['Normal']))
        story.append(Paragraph(f"Total Grades: {len(all_grades)}", styles['Normal']))
        
        if all_grades:
            overall_avg = sum(grade.note for grade in all_grades) / len(all_grades)
            story.append(Paragraph(f"Overall Average Grade: {overall_avg:.2f}/100", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{current_user.name}_general_report.pdf",
            mimetype='application/pdf'
        )

    @app.route('/notes')
    @login_required
    def manage_notes():
        notes = Note.query.filter_by(user_id=current_user.id).all()
        return render_template('notes.html', notes=notes)

    @app.route('/notes/add', methods=['GET', 'POST'])
    @login_required
    def add_note():
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            
            note = Note(title=title, content=content, user_id=current_user.id)
            db.session.add(note)
            db.session.commit()
            
            flash('Not başarıyla eklendi!', 'success')
            return redirect(url_for('manage_notes'))
        
        return render_template('add_note.html')

    @app.route('/notes/edit/<int:note_id>', methods=['GET', 'POST'])
    @login_required
    def edit_note(note_id):
        note = Note.query.get_or_404(note_id)
        
        if note.user_id != current_user.id:
            abort(403)
        
        if request.method == 'POST':
            note.title = request.form.get('title')
            note.content = request.form.get('content')
            db.session.commit()
            
            flash('Not başarıyla güncellendi!', 'success')
            return redirect(url_for('manage_notes'))
        
        return render_template('edit_note.html', note=note)

    @app.route('/notes/delete/<int:note_id>', methods=['POST'])
    @login_required
    def delete_note(note_id):
        note = Note.query.get_or_404(note_id)
        
        if note.user_id != current_user.id:
            flash('Sadece kendi notlarınızı silebilirsiniz!', 'error')
            return redirect(url_for('manage_notes'))
        
        db.session.delete(note)
        db.session.commit()
        flash('Not başarıyla silindi!', 'success')
        return redirect(url_for('manage_notes'))

    @app.route('/announcements')
    @login_required
    def view_announcements():
        announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
        return render_template('announcements.html', announcements=announcements)

    @app.route('/teacher/announcements')
    @login_required
    @teacher_required
    def manage_announcements():
        announcements = Announcement.query.filter_by(author_id=current_user.id).all()
        return render_template('teacher/announcements.html', announcements=announcements)

    @app.route('/teacher/announcements/add', methods=['GET', 'POST'])
    @login_required
    @teacher_required
    def add_announcement():
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            
            announcement = Announcement(title=title, content=content, author_id=current_user.id)
            db.session.add(announcement)
            db.session.commit()
            
            flash('Duyuru başarıyla yayınlandı!', 'success')
            return redirect(url_for('manage_announcements'))
        
        return render_template('teacher/add_announcement.html')

    @app.route('/teacher/announcements/edit/<int:announcement_id>', methods=['GET', 'POST'])
    @login_required
    @teacher_required
    def edit_announcement(announcement_id):
        announcement = Announcement.query.get_or_404(announcement_id)
        
        if announcement.author_id != current_user.id:
            abort(403)
        
        if request.method == 'POST':
            announcement.title = request.form.get('title')
            announcement.content = request.form.get('content')
            db.session.commit()
            
            flash('Duyuru başarıyla güncellendi!', 'success')
            return redirect(url_for('manage_announcements'))
        
        return render_template('teacher/edit_announcement.html', announcement=announcement)

    @app.route('/teacher/announcements/delete/<int:announcement_id>', methods=['POST'])
    @login_required
    @teacher_required
    def delete_announcement(announcement_id):
        announcement = Announcement.query.get_or_404(announcement_id)
        
        if announcement.author_id != current_user.id:
            flash('Sadece kendi duyurularınızı silebilirsiniz!', 'error')
            return redirect(url_for('manage_announcements'))
        
        db.session.delete(announcement)
        db.session.commit()
        flash('Duyuru başarıyla silindi!', 'success')
        return redirect(url_for('manage_announcements')) 