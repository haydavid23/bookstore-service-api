import os
import jwt
from flask import g, Blueprint, jsonify, request
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from auth import login_required
from models import UserProfile, CreditCard
from blueprints.profile.dto.profile_dto import (
    CreateProfileDTO,
    ProfileResponseDTO,
    UpdateProfileDTO,
    CreateCreditCardDTO,
    CreditCardResponseDTO,
)

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a valid JSON"}), 400

    try:
        profile_dto = CreateProfileDTO.from_dict(data)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    user = UserProfile(
        username=profile_dto.username,
        email=profile_dto.email,
        address=profile_dto.address,
        first_name=profile_dto.first_name,
        last_name=profile_dto.last_name,
        password=generate_password_hash(profile_dto.password),
        role=profile_dto.role,
    )

    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username or email already exists"}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while creating user"}), 500

    response_dto = ProfileResponseDTO.from_model(user)
    return jsonify(response_dto.to_dict()), 201

@profile_bp.route("/users/<username>", methods=["GET"])
@login_required
def get_user(username):
    if g.current_user["username"] != username and g.current_user["role"] != "admin":
        return jsonify({"error": "Cannot access another user's profile"}), 403
    user = UserProfile.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    response_dto = ProfileResponseDTO.from_model(user)
    return jsonify(response_dto.to_dict()), 200

@profile_bp.route("/users/<username>", methods=["PATCH"])
@login_required
def update_user(username):
    if g.current_user["username"] != username and g.current_user["role"] != "admin":
        return jsonify({"error": "Cannot access another user's profile"}), 403
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        profile_dto = UpdateProfileDTO.from_dict(data)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
        
    user = UserProfile.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    updates = profile_dto.updates.copy()
        
    if "password" in updates:
        updates["password"] = generate_password_hash(updates["password"])

    for field, value in updates.items():
        setattr(user, field, value)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username already exists"}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while updating user"}), 500

    response_dto = ProfileResponseDTO.from_model(user)
    return jsonify(response_dto.to_dict()), 200

@profile_bp.route("/users/<username>/credit-cards", methods=["POST"])
@login_required
def create_credit_card(username):
    if g.current_user["username"] != username and g.current_user["role"] != "admin":
        return jsonify({"error": "Cannot access another user's profile"}), 403
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        credit_card_dto = CreateCreditCardDTO.from_dict(data)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    user = UserProfile.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    credit_card = CreditCard(
        card_number=credit_card_dto.card_number,
        expiration_date=credit_card_dto.expiration_date,
        user_profile_id=user.id,
        cvv=credit_card_dto.cvv,
    )

    db.session.add(credit_card)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Credit card already exists"}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while creating credit card"}), 500

    response_dto = CreditCardResponseDTO.from_model(credit_card)
    return jsonify(response_dto.to_dict()), 201

@profile_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not username.strip():
        return jsonify({"error": "username is required"}), 400

    if not isinstance(password, str) or not password:
        return jsonify({"error": "password is required"}), 400
    user = UserProfile.query.filter_by(username=username.strip()).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password"}), 401

    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        return jsonify({"error": "JWT secret is not configured"}), 500

    payload = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=2),
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    return jsonify({"token": token}), 200
