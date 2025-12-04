from datetime import datetime, timedelta
from models import Appointment, DoctorProfile, MedicalService, db, Users
from flask import jsonify, Blueprint, request, current_app
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
import json
import redis

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


def get_redis_client():
    return redis.Redis(
        host=current_app.config["REDIS_HOST"],
        port=current_app.config["REDIS_PORT"],
        decode_responses=True,
    )


@auth_bp.route("/user/<user_id>", methods=["GET"])
def get_user(user_id):
    user = Users.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(
        {
            "Email": f"{user.email}",
            "Name": f"{user.last_name} {user.first_name}",
            "Role": f"{user.role}",
        }
    )


@auth_bp.route("/users", methods=["GET"])
def get_users():
    users = Users.query.all()
    response = []

    for user in users:
        full_name = "Unknown"
        if user.last_name and user.first_name:
            full_name = f"{user.last_name} {user.first_name}"
        user_data = {
            "Email": user.email,
            "Name": full_name,
            "Role": user.role,
            "ID": user.id,
        }
        response.append(user_data)
    return jsonify(response), 200


@auth_bp.route("/user/<get_id>", methods=["PUT"])
@jwt_required()
def modify_user(get_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Only admins can modify user roles"}), 403

    user = Users.query.filter_by(id=get_id).first()
    if not user:
        return jsonify({"message": "That is not an valid user"}), 404

    data = request.get_json()
    role = data.get("role")

    valid_roles = ["client", "admin", "doctor"]
    if not data or role not in valid_roles:
        return jsonify({"message": f"Invalid role. Allowed: {valid_roles}"}), 400

    user.role = role

    try:
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "User role modified successfully",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "role": user.role,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating user", "error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Please enter email and password"}), 400
    user = Users.query.filter_by(email=data.get("email")).first()
    if not user:
        return jsonify({"message": "Email or password incorrect"}), 400

    if user.check_password(data.get("password")):
        access_token = create_access_token(
            identity=user.id, additional_claims={"role": user.role}
        )
        return (
            jsonify(
                {
                    "message": "Login succesfully",
                    "id": f"{user.id}",
                    "role": f"{user.role}",
                    "username": f"{user.username}",
                    "access_token": f"{access_token}",
                }
            ),
            200,
        )
    else:
        return jsonify({"message": "Email or password incorrect"}), 401


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if (
        not data
        or not data.get("email")
        or not data.get("password")
        or not data.get("username")
    ):
        return jsonify({"message": "Please enter email, username and password"}), 400
    user = Users.query.filter_by(email=data.get("email")).first()
    if user:
        return (
            jsonify({"message": "User with that email already exists. Please login"}),
            409,
        )
    if Users.query.filter_by(username=data.get("username")).first():
        return (
            jsonify(
                {"message": "User with that username already exists. Please login"}
            ),
            409,
        )

    user = Users(email=data.get("email"), username=data.get("username"))
    user.set_password(data.get("password"))

    last_name = data.get("last_name")
    first_name = data.get("first_name")

    if not last_name or not first_name:
        return jsonify({"message": "Please enter valid First and Last name"}), 400

    user.set_name(last_name, first_name)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating user", "error": str(e)}), 500

    return jsonify({"message": "User created succesfully", "id": user.id}), 201


@auth_bp.route("/services", methods=["POST"])
@jwt_required()
def new_service():
    claims = get_jwt()
    if not claims["role"] == "admin":
        return jsonify({"message": "Only an admin can create doctors"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"message": "Please enter valid data"}), 400

    name = data.get("name")
    species = data.get("species")
    duration = data.get("duration")
    price = data.get("price")

    if not name:
        return jsonify({"message": "Please enter valid name for consultation"}), 400
    if not species:
        return jsonify({"message": "Please enter valid name species"}), 400
    if not duration:
        return jsonify({"message": "Please enter valid duration"}), 400
    if not price:
        return jsonify({"message": "Please enter valid price"}), 400

    new_service = MedicalService(name, species, duration, price)
    try:
        db.session.add(new_service)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating new service", "error": str(e)}), 500

    try:
        r = get_redis_client()
        r.delete("services:all")
    except Exception as e:
        print(f"Warning: Could not invalidate cache. Redis error: {str(e)}")

    return (
        jsonify({"message": "Service created succesfully", "id": new_service.id}),
        201,
    )


@auth_bp.route("/services", methods=["GET"])
def list_services():
    r = get_redis_client()
    cache_key = "services:all"
    rezultat = None

    try:
        cached_data = r.get(cache_key)
        if cached_data:
            print("Data fetched from Redis Cache")
            return jsonify(json.loads(cached_data)), 200
    except redis.RedisError as e:
        print(f"Redis error: {e}")

    services = MedicalService.query.all()
    rezultat = []

    for x in services:
        y = {
            "id": x.id,
            "name": f"{x.name}",
            "species": f"{x.species}",
            "duration": f"{x.duration}",
            "price": f"{x.price}",
        }
        rezultat.append(y)

    if rezultat:
        try:
            r.setex(cache_key, 60, json.dumps(rezultat))
        except redis.RedisError:
            pass

        return jsonify(rezultat), 200
    else:
        return jsonify({"message": "There is no service to list"}), 404


@auth_bp.route("/services/<service_id>", methods=["PUT"])
def modify_service(service_id):
    service = MedicalService.query.filter_by(id=service_id).first()

    if not service:
        return jsonify({"message": "This service does not exists"}), 404

    data = request.get_json()
    if not data or not data.get("price") or not data.get("duration"):
        return jsonify({"message": "Please enter price and duration"}), 400

    service.price = data.get("price")
    service.duration = data.get("duration")

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating service", "error": str(e)}), 500

    try:
        r = get_redis_client()
        r.delete("services:all")
    except Exception as e:
        print(f"Warning: Redis error on modify: {str(e)}")

    return (
        jsonify(
            {
                "message": "Service updated successfully",
                "service": {
                    "id": service.id,
                    "name": service.name,
                    "price": service.price,
                    "duration": service.duration,
                },
            }
        ),
        200,
    )


@auth_bp.route("/services/<service_id>", methods=["DELETE"])
@jwt_required()
def delete_service(service_id):
    claims = get_jwt()
    if not claims["role"] == "admin":
        return jsonify({"message": "Only an admin can create doctors"}), 403

    service = MedicalService.query.filter_by(id=service_id).first()
    if not service:
        return jsonify({"message": "This service does not exist"}), 404

    try:
        db.session.delete(service)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting service", "error": str(e)}), 500

    try:
        r = get_redis_client()
        r.delete("services:all")
    except Exception as e:
        print(f"Warning: Redis error on delete: {str(e)}")
    return jsonify({"message": "Service deleted successfully"}), 200


@auth_bp.route("/doctors", methods=["POST"])
@jwt_required()
def create_doctor():
    claims = get_jwt()
    if not claims["role"] == "admin":
        return jsonify({"message": "Only an admin can create doctors"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"message": "Please enter valid data"}), 400

    user_id = data.get("user_id")
    specialization = data.get("specialization")
    bio = data.get("bio")

    if not user_id or not specialization or not bio:
        return jsonify({"message": "Please enter all input fields"}), 400

    user = Users.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    existing_doctor = DoctorProfile.query.filter_by(user_id=user_id).first()

    try:
        if existing_doctor:
            existing_doctor.specialization = specialization
            existing_doctor.bio = bio

            db.session.commit()
            return (
                jsonify(
                    {
                        "message": "Doctor profile updated successfully",
                        "id": existing_doctor.id,
                    }
                ),
                200,
            )
        else:
            new_doctor = DoctorProfile(
                user_id=user_id, specialization=specialization, bio=bio
            )
            db.session.add(new_doctor)
            db.session.commit()

            return (
                jsonify(
                    {
                        "message": "Doctor profile created successfully",
                        "id": new_doctor.id,
                    }
                ),
                201,
            )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error processing request", "error": str(e)}), 500


@auth_bp.route("/doctors", methods=["GET"])
def list_doctors():
    doctors = DoctorProfile.query.all()
    response = []
    for doctor in doctors:
        full_name = "Unknown"
        if doctor.user:
            full_name = f"{doctor.user.last_name} {doctor.user.first_name}"

        doctor_data = {
            "doctor_id": doctor.id,
            "user_id": doctor.user_id,
            "name": full_name,
            "specialization": doctor.specialization,
            "bio": doctor.bio,
        }
        response.append(doctor_data)
    return jsonify(response), 200


# Appointments
@auth_bp.route("/appointments", methods=["POST"])
def create_appointment():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Please enter valid data"}), 400

    start_time_raw = data.get("start_time")
    doctor_id = data.get("doctor_id")
    client_id = data.get("client_id")
    service_id = data.get("service_id")
    status = data.get("status", "scheduled")

    if not start_time_raw or not doctor_id or not client_id or not service_id:
        return jsonify({"message": "Please enter valid data for appointment"}), 400

    service = MedicalService.query.filter_by(id=service_id).first()
    client = Users.query.filter_by(id=client_id).first()
    doctor = DoctorProfile.query.filter_by(id=doctor_id).first()

    try:
        start_time = datetime.fromisoformat(start_time_raw)
    except ValueError:
        return (
            jsonify(
                {"message": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}
            ),
            400,
        )

    if not service:
        return jsonify({"message": "This service does not exist"}), 404
    if not client:
        return jsonify({"message": "This client does not exist"}), 404
    if not doctor:
        return jsonify({"message": "This doctor does not exist"}), 404

    durata = timedelta(minutes=service.duration)
    end_time = start_time + durata

    existing_appointment = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status != "cancelled",
        Appointment.start_time < end_time,
        Appointment.end_time > start_time,
    ).first()

    if existing_appointment:
        return (
            jsonify(
                {
                    "message": "Doctor is not available at this time",
                    "conflict_with": f"{existing_appointment.start_time} - {existing_appointment.end_time}",
                }
            ),
            409,
        )

    new_appointment = Appointment(
        start_time=start_time,
        end_time=end_time,
        status=status,
        doctor_id=doctor_id,
        client_id=client_id,
        service_id=service_id,
    )

    try:
        db.session.add(new_appointment)
        db.session.commit()
        return jsonify({"message": "Appointment created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error processing request", "error": str(e)}), 500


@auth_bp.route("/appointments", methods=["GET"])
def show_appointments():
    client_id = request.args.get("client_id")
    doctor_id = request.args.get("doctor_id")

    query = Appointment.query

    if client_id:
        query = query.filter_by(client_id=client_id)
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)

    appointments = query.all()

    if not appointments:
        return jsonify([]), 200

    response = []

    for x in appointments:
        doctor_full_name = "Unknown"
        if x.doctor and x.doctor.user:
            doctor_full_name = f"{x.doctor.user.last_name} {x.doctor.user.first_name}"

        client_full_name = "Unknown"
        if x.client:
            client_full_name = f"{x.client.last_name} {x.client.first_name}"

        appointment = {
            "id": x.id,
            "start_time": x.start_time.isoformat(),
            "end_time": x.end_time.isoformat(),
            "status": x.status,
            "doctor_name": doctor_full_name,
            "service_name": x.service.name if x.service else "Service deleted",
            "client_name": client_full_name,
            "price": x.service.price if x.service else 0,
        }

        response.append(appointment)

    if response:
        return jsonify(response), 200


@auth_bp.route("/appointment/<appointment_id>", methods=["PUT"])
def update_appointment_status(appointment_id):
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    if not appointment:
        return jsonify({"message": "This appointment does not exist"}), 404

    data = request.get_json()
    status = data.get("status")
    if not data or not status:
        return jsonify({"message": "Please enter status"}), 400

    valid_statuses = ["scheduled", "completed", "cancelled"]
    if status not in valid_statuses:
        return jsonify({"message": f"Invalid status. Allowed: {valid_statuses}"}), 400

    appointment.status = status

    try:
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Status modified successfully",
                    "new_Status": appointment.status,
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error processing request", "error": str(e)}), 500
