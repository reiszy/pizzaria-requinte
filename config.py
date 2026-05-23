import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao-requinte")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "pizzaria.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
    BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    DATABASE_DIR = os.path.join(BASE_DIR, "database")
