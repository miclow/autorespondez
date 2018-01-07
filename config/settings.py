from datetime import timedelta

DEBUG = True

SERVER_NAME = 'localhost:8000'
SECRET_KEY = 'insecurekeychange'

# Flask Mail
MAIL_DEFAULT_SENDER = 'contact@local.host'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = 'test@gmail.com'
MAIL_PASSWORD = 'livepassword'
MAIL_USE_TLS = True
MAIL_USE_SSL = False

# Celery
CELERY_BROKER_URL = 'redis://:deV1234@redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://:deV1234@redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_REDIS_MAX_CONNECTIONS = 5

# SQLAlchemy
db_uri = 'postgresql://autorespondez:Auto!@#4@postgres:5432/autorespondez'
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = False

#user
SEED_ADMIN_EMAIL = 'dev@local.host'
SEED_ADMIN_EMAIL = 'devpassword'
REMEMBER_COOKIE_DURATION = timedelta(days=90)