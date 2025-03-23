from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from models import db  # Import only models here
from resources.Auth import Register, Login  # Import API resource classes
from resources.Disasters import DisasterReportAPI
from resources.Aid import AidRequestAPI
from resources.Volunteers import VolunteerAssignmentAPI

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@localhost/disaster_relief"
app.config["JWT_SECRET_KEY"] = "supersecretkey"

socketio = SocketIO(app, cors_allowed_origins="*")

db.init_app(app)
api = Api(app)
jwt = JWTManager(app)

# ✅ Registering Correct API Resource Classes
api.add_resource(Register, "/auth/register")
api.add_resource(Login, "/auth/login")
api.add_resource(DisasterReportAPI, "/disasters")
api.add_resource(AidRequestAPI, "/aid_requests")
api.add_resource(VolunteerAssignmentAPI, "/volunteer_assignments")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
