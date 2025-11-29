from models import db, Users
from flask import jsonify, Blueprint, request

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


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


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Please enter email and password"}), 400
    user = Users.query.filter_by(email=data.get("email")).first()
    if not user:
        return jsonify({"message": "Email or password incorrect"}), 400

    if user.check_password(data.get("password")):
        return (
            jsonify(
                {
                    "message": "Login succesfully",
                    "id": f"{user.id}",
                    "role": f"{user.role}",
                    "username": f"{user.username}",
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
