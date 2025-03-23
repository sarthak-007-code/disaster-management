from flask_restful import Resource
from flask import request, jsonify
from models import db, VolunteerAssignment

class VolunteerAssignmentAPI(Resource):
    def post(self):
        data = request.json
        new_assignment = VolunteerAssignment(
            volunteer_id=data["volunteer_id"],
            aid_request_id=data["aid_request_id"],
            status="pending"
        )
        db.session.add(new_assignment)
        db.session.commit()
        return jsonify({"message": "Volunteer assigned successfully"})

    def get(self):
        assignments = VolunteerAssignment.query.filter_by(status="pending").all()
        return jsonify([
            {"id": a.id, "volunteer": a.volunteer_id, "aid_request": a.aid_request_id, "status": a.status}
            for a in assignments
        ])
