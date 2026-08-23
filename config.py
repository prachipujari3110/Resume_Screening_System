import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

MYSQL_HOST = "localhost"
MYSQL_PORT = 3308
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DATABASE = "resume_screening"

SECRET_KEY = "resume-screening-project-2026"

UPLOAD_RESUMES = os.path.join(BASE_DIR, "uploads", "resumes")
UPLOAD_PHOTOS = os.path.join(BASE_DIR, "uploads", "photos")
