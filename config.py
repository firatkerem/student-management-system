import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # Geliştirme için SQLite kullan, production'da MySQL kullan
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///student_management.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 