from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User
from routes import init_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Bu sayfaya erişmek için giriş yapmalısınız.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    init_routes(app)
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        db.create_all()
        
        if not User.query.first():
            from werkzeug.security import generate_password_hash
            
            teacher = User(
                name='Test Öğretmen',
                email='teacher@test.com',
                password_hash=generate_password_hash('password'),
                role='teacher'
            )
            db.session.add(teacher)
            
            student = User(
                name='Test Öğrenci',
                email='student@test.com',
                password_hash=generate_password_hash('password'),
                role='student'
            )
            db.session.add(student)
            
            db.session.commit()
            print("Test kullanıcıları oluşturuldu:")
            print("Öğretmen: teacher@test.com / password")
            print("Öğrenci: student@test.com / password")
    
    app.run(host='0.0.0.0', port=8080, debug=True) 