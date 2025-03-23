from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token


db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    user_type = db.Column(db.Enum("victim", "volunteer", "ngo"), nullable=False)
    location = db.Column(db.String(255))  # Can be stored as 'latitude,longitude'
    skills = db.Column(db.String(255), nullable=True)  # For volunteers
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def generate_token(self):
        return create_access_token(identity=self.id)

bcrypt = Bcrypt()

class DisasterReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reported_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disaster_type = db.Column(db.Enum("flood", "earthquake", "fire"), nullable=False)
    severity = db.Column(db.Enum("low", "medium", "high"), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum("active", "resolved"), default="active")

    reporter = db.relationship("User", backref="reports")

class AidRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requested_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disaster_id = db.Column(db.Integer, db.ForeignKey('disaster_report.id'), nullable=False)
    resource_type = db.Column(db.Enum("food", "water", "medical aid", "shelter"), nullable=False)
    priority = db.Column(db.Enum("high", "medium", "low"), default="medium")
    status = db.Column(db.Enum("pending", "fulfilled"), default="pending")

    requester = db.relationship("User", backref="aid_requests")
    disaster = db.relationship("DisasterReport", backref="aid_requests")

class VolunteerAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    aid_request_id = db.Column(db.Integer, db.ForeignKey('aid_request.id'), nullable=False)
    status = db.Column(db.Enum("pending", "accepted", "completed"), default="pending")

    volunteer = db.relationship("User", backref="assignments")
    aid_request = db.relationship("AidRequest", backref="assignments")
