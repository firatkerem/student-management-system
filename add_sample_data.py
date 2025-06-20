#!/usr/bin/env python3

from app import create_app
from models import db, User, Course, Enrollment, Grade, Note, Announcement
from datetime import datetime, timedelta
import random

def add_sample_data():
    app = create_app()
    with app.app_context():
        teachers = [
            {"name": "Ahmet Yılmaz", "email": "ahmet.yilmaz@okul.edu.tr", "password": "123456", "role": "teacher"},
            {"name": "Fatma Demir", "email": "fatma.demir@okul.edu.tr", "password": "123456", "role": "teacher"},
            {"name": "Mehmet Kaya", "email": "mehmet.kaya@okul.edu.tr", "password": "123456", "role": "teacher"},
            {"name": "Ayşe Özkan", "email": "ayse.ozkan@okul.edu.tr", "password": "123456", "role": "teacher"},
            {"name": "Ali Çelik", "email": "ali.celik@okul.edu.tr", "password": "123456", "role": "teacher"}
        ]
        
        for t in teachers:
            existing = User.query.filter_by(email=t["email"]).first()
            if not existing:
                user = User(name=t["name"], email=t["email"], role=t["role"])
                user.set_password(t["password"])
                db.session.add(user)
        
        db.session.commit()
        
        students = [
            {"name": "Baran Fırat", "email": "baran.firat@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Zeynep Arslan", "email": "zeynep.arslan@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Emre Yıldız", "email": "emre.yildiz@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Selin Öztürk", "email": "selin.ozturk@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Can Demir", "email": "can.demir@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Elif Kaya", "email": "elif.kaya@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Burak Şahin", "email": "burak.sahin@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Merve Aydın", "email": "merve.aydin@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Deniz Özkan", "email": "deniz.ozkan@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Gizem Çelik", "email": "gizem.celik@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Kaan Yılmaz", "email": "kaan.yilmaz@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Sude Demir", "email": "sude.demir@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Ege Kaya", "email": "ege.kaya@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Defne Öztürk", "email": "defne.ozturk@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Arda Şahin", "email": "arda.sahin@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Ada Aydın", "email": "ada.aydin@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Mert Özkan", "email": "mert.ozkan@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Yağız Çelik", "email": "yagiz.celik@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Nehir Yılmaz", "email": "nehir.yilmaz@okul.edu.tr", "password": "123456", "role": "student"},
            {"name": "Atlas Demir", "email": "atlas.demir@okul.edu.tr", "password": "123456", "role": "student"}
        ]
        
        for s in students:
            existing = User.query.filter_by(email=s["email"]).first()
            if not existing:
                user = User(name=s["name"], email=s["email"], role=s["role"])
                user.set_password(s["password"])
                db.session.add(user)
        
        db.session.commit()
        
        courses = [
            Course(name="Matematik 101", description="Temel matematik dersi", teacher_id=1),
            Course(name="Fizik 101", description="Temel fizik dersi", teacher_id=1),
            Course(name="Kimya 101", description="Temel kimya dersi", teacher_id=2),
            Course(name="Biyoloji 101", description="Temel biyoloji dersi", teacher_id=2),
            Course(name="Türkçe 101", description="Temel Türkçe dersi", teacher_id=3),
            Course(name="İngilizce 101", description="Temel İngilizce dersi", teacher_id=3),
            Course(name="Tarih 101", description="Temel tarih dersi", teacher_id=4),
            Course(name="Coğrafya 101", description="Temel coğrafya dersi", teacher_id=4),
            Course(name="Bilgisayar Bilimi", description="Programlama ve algoritma", teacher_id=5),
            Course(name="Veri Yapıları", description="Veri yapıları ve algoritmalar", teacher_id=5),
            Course(name="Veritabanı Sistemleri", description="SQL ve veritabanı yönetimi", teacher_id=5),
            Course(name="Web Geliştirme", description="HTML, CSS, JavaScript", teacher_id=5),
            Course(name="Matematik 201", description="İleri matematik dersi", teacher_id=1),
            Course(name="Fizik 201", description="İleri fizik dersi", teacher_id=1),
            Course(name="Kimya 201", description="İleri kimya dersi", teacher_id=2)
        ]
        
        for course in courses:
            existing = Course.query.filter_by(name=course.name).first()
            if not existing:
                db.session.add(course)
        
        db.session.commit()
        
        all_students = User.query.filter_by(role="student").all()
        all_courses = Course.query.all()
        
        for student in all_students:
            num_courses = random.randint(3, 6)
            selected_courses = random.sample(all_courses, num_courses)
            
            for course in selected_courses:
                existing_enrollment = Enrollment.query.filter_by(
                    student_id=student.id, 
                    course_id=course.id
                ).first()
                
                if not existing_enrollment:
                    enrollment_date = datetime.now() - timedelta(days=random.randint(1, 90))
                    enrollment = Enrollment(
                        student_id=student.id,
                        course_id=course.id,
                        enrolled_at=enrollment_date
                    )
                    db.session.add(enrollment)
        
        db.session.commit()
        
        all_enrollments = Enrollment.query.all()
        
        for enrollment in all_enrollments:
            if random.random() < 0.8:
                grade_value = random.randint(0, 100)
                grade_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                grade = Grade(
                    student_id=enrollment.student_id,
                    course_id=enrollment.course_id,
                    note=grade_value,
                    created_at=grade_date
                )
                db.session.add(grade)
        
        db.session.commit()
        
        all_users = User.query.all()
        note_titles = [
            "Önemli toplantı notları",
            "Ders planı",
            "Ödev kontrol listesi",
            "Sınav tarihleri",
            "Öğrenci değerlendirmeleri",
            "Proje fikirleri",
            "Araştırma notları",
            "Kitap önerileri",
            "Web sitesi kaynakları",
            "Yazılım araçları"
        ]
        
        note_contents = [
            "Bu hafta öğrencilerle birebir görüşmeler yapılacak.",
            "Matematik dersinde geometri konusuna odaklanılmalı.",
            "Fizik laboratuvarı için yeni ekipman gerekli.",
            "Kimya sınavı için soru bankası hazırlanmalı.",
            "Biyoloji projesi için arazi çalışması planlanmalı.",
            "Türkçe dersinde kompozis yazma teknikleri öğretilecek.",
            "İngilizce konuşma pratiği için yabancı öğretmen bulunmalı.",
            "Tarih dersinde görsel materyaller kullanılmalı.",
            "Coğrafya için harita çalışması yapılmalı.",
            "Bilgisayar dersinde proje tabanlı öğrenme uygulanmalı."
        ]
        
        for user in all_users:
            num_notes = random.randint(2, 5)
            for i in range(num_notes):
                title = random.choice(note_titles)
                content = random.choice(note_contents)
                note_date = datetime.now() - timedelta(days=random.randint(1, 60))
                
                note = Note(
                    title=title,
                    content=content,
                    user_id=user.id,
                    created_at=note_date
                )
                db.session.add(note)
        
        db.session.commit()
        
        announcement_titles = [
            "Sınav Tarihleri Güncellendi",
            "Yeni Kurs Kayıtları Başladı",
            "Laboratuvar Çalışması İptal",
            "Ödev Teslim Tarihi Uzatıldı",
            "Veli Toplantısı Duyurusu",
            "Okul Gezisi Planlanıyor",
            "Spor Turnuvası Duyurusu",
            "Kütüphane Saatleri Değişti",
            "Teknoloji Semineri",
            "Sanat Sergisi Açılışı"
        ]
        
        announcement_contents = [
            "Final sınavları 15-20 Haziran tarihleri arasında yapılacaktır.",
            "Yeni dönem kurs kayıtları 1 Eylül'de başlayacaktır.",
            "Bu hafta laboratuvar çalışması teknik arıza nedeniyle iptal edilmiştir.",
            "Ödev teslim tarihi bir hafta uzatılmıştır.",
            "Veli toplantısı 25 Haziran'da yapılacaktır.",
            "Müze gezisi 30 Haziran'da planlanmaktadır.",
            "Okullar arası spor turnuvası 10 Temmuz'da başlayacaktır.",
            "Kütüphane artık hafta sonu da açık olacaktır.",
            "Teknoloji semineri 5 Temmuz'da düzenlenecektir.",
            "Öğrenci sanat sergisi 20 Temmuz'da açılacaktır."
        ]
        
        teachers = User.query.filter_by(role="teacher").all()
        
        for teacher in teachers:
            num_announcements = random.randint(1, 3)
            for i in range(num_announcements):
                title = random.choice(announcement_titles)
                content = random.choice(announcement_contents)
                announcement_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                announcement = Announcement(
                    title=title,
                    content=content,
                    author_id=teacher.id,
                    created_at=announcement_date
                )
                db.session.add(announcement)
        
        db.session.commit()
        
        print("Örnek veriler başarıyla eklendi!")
        print(f"Toplam {len(teachers)} öğretmen eklendi")
        print(f"Toplam {len(students)} öğrenci eklendi")
        print(f"Toplam {len(courses)} kurs eklendi")
        print(f"Toplam {Enrollment.query.count()} kurs kaydı eklendi")
        print(f"Toplam {Grade.query.count()} not eklendi")
        print(f"Toplam {Note.query.count()} kişisel not eklendi")
        print(f"Toplam {Announcement.query.count()} duyuru eklendi")

if __name__ == "__main__":
    add_sample_data() 