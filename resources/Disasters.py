from flask_restful import Resource
from flask import request, jsonify
from models import db, DisasterReport

class DisasterReportAPI(Resource):
    def post(self):
        data = request.json
        new_report = DisasterReport(
            reported_by=data["reported_by"],
            disaster_type=data["disaster_type"],
            severity=data["severity"],
            location=data["location"],
            description=data.get("description", "")
        )
        db.session.add(new_report)
        db.session.commit()
        return jsonify({"message": "Disaster report submitted successfully"})

    def get(self):
        reports = DisasterReport.query.all()
        return jsonify([
            {"id": r.id, "type": r.disaster_type, "location": r.location, "severity": r.severity}
            for r in reports
        ])
