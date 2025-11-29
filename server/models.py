from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def get_uuid():
    return uuid4().hex


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(345), unique=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(32), nullable=True)
    last_name = db.Column(db.String(32), nullable=True)

    role = db.Column(db.String(20), default="client")

    # Leaga user de profilul de medic
    doctor_profile = db.relationship("DoctorProfile", backref="user", uselist=False)

    def set_password(self, password_text):
        self.password = generate_password_hash(password_text)

    def check_password(self, password_text):
        return check_password_hash(self.password, password_text)

    def set_name(self, last_name, first_name):
        self.first_name = first_name
        self.last_name = last_name


class MedicalService(db.Model):
    __tablename__ = "medical_services"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Service {self.name}"


doctor_services = db.Table(
    "doctor_services",
    db.Column(
        "doctor_id",
        db.String(32),
        db.ForeignKey("doctor_profiles.id"),
        primary_key=True,
    ),
    db.Column(
        "service_id", db.Integer, db.ForeignKey("medical_services.id"), primary_key=True
    ),
)


class DoctorProfile(db.Model):
    __tablename__ = "doctor_profiles"
    id = db.Column(db.String(32), primary_key=True, default=get_uuid)

    user_id = db.Column(
        db.String(32), db.ForeignKey("users.id"), unique=True, nullable=False
    )
    specialization = db.Column(db.String(100))
    bio = db.Column(db.Text)

    # Many-to-Many, lista de obiecte MedicalService
    services = db.relationship(
        "MedicalService", secondary=doctor_services, backref="doctors"
    )

    def __repr__(self):
        return f"Dr. {self.user_id}"


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.String(32), primary_key=True, default=get_uuid)
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    status = db.Column(db.String(32), default="available", nullable=False)

    doctor_id = db.Column(
        db.String(32), db.ForeignKey("doctor_profiles.id"), nullable=False
    )
    client_id = db.Column(db.String(32), db.ForeignKey("users.id"))
    service_id = db.Column(db.Integer, db.ForeignKey("medical_services.id"))

    # ORM
    doctor = db.relationship("DoctorProfile", backref="appointments")
    client = db.relationship("Users", backref="appointments")
    service = db.relationship("MedicalService")

    def __repr__(self):
        return f"Appointment {self.start_time} - {self.status}"
