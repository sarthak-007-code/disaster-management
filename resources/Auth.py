from flask_restful import Resource
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User

class Register(Resource):
    def post(self):
        data = request.json
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"message": "Email already registered"}), 400

        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            user_type=data["user_type"],
            location=data.get("location", ""),
            skills=data.get("skills", "")
        )
        user.set_password(data["password"])

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"})

class Login(Resource):
    def post(self):
        data = request.json
        user = User.query.filter_by(email=data["email"]).first()

        if user and user.check_password(data["password"]):
            token = create_access_token(identity=user.id)
            return jsonify({"token": token, "user_type": user.user_type})

        return jsonify({"message": "Invalid credentials"}), 401
