from flask_restful import Resource
from flask import request, jsonify
from models import db, AidRequest

class AidRequestAPI(Resource):
    def post(self):
        data = request.json
        new_request = AidRequest(
            requested_by=data["requested_by"],
            disaster_id=data["disaster_id"],
            resource_type=data["resource_type"],
            priority=data.get("priority", "medium"),
            status="pending"
        )
        db.session.add(new_request)
        db.session.commit()
        return jsonify({"message": "Aid request submitted successfully"})

    def get(self):
        requests = AidRequest.query.filter_by(status="pending").all()
        return jsonify([
            {"id": r.id, "resource": r.resource_type, "priority": r.priority, "status": r.status}
            for r in requests
        ])
