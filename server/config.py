from dotenv import load_dotenv
import os
import redis

load_dotenv()


class ApplicationConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "default_jwt_key")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "password")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    db_name = os.environ.get("POSTGRES_DB", "veterinary_db")

    SQLALCHEMY_DATABASE_URI = f"postgresql://{user}:{password}@{host}:5432/{db_name}"

    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = os.environ.get("REDIS_PORT", 6379)

    SESSION_REDIS = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
