import os
import requests
from flask import Flask, request, jsonify, make_response, send_from_directory
import sqlite3

app = Flask(__name__)

# Google API key (store in environment variables in production)
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Database setup
DB_PATH = "reports.db"

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            description TEXT,
            latitude FLOAT,
            longitude FLOAT,
            photo_path TEXT,
            status TEXT DEFAULT 'Not Reported Yet'
        )''')
        conn.commit()
        conn.close()

init_db()

# Homepage with role selector
@app.route('/')
def home():
    role = request.cookies.get('role')
    if role == 'user':
        return app.send_static_file('report.html')
    elif role == 'volunteer':
        return app.send_static_file('volunteer.html')
    return app.send_static_file('index.html')

# Set role and redirect
@app.route('/set-role', methods=['POST'])
def set_role():
    role = request.form.get('role')
    resp = make_response('')
    if role == 'user':
        resp = make_response(app.send_static_file('report.html'))
    elif role == 'volunteer':
        resp = make_response(app.send_static_file('volunteer.html'))
    resp.set_cookie('role', role)
    return resp

# User interface for reporting disasters
@app.route('/report-page')
def report_page():
    role = request.cookies.get('role')
    if role != 'user':
        return app.send_static_file('index.html')
    return app.send_static_file('report.html')

# Volunteer interface for viewing disasters
@app.route('/volunteer-page')
def volunteer_page():
    role = request.cookies.get('role')
    if role != 'volunteer':
        return app.send_static_file('index.html')
    return app.send_static_file('volunteer.html')

# Submit a report
@app.route('/report', methods=['POST'])
def report_disaster():
    data = request.get_json()
    location = data['location']
    description = data['description']
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # If latitude and longitude are not provided, geocode the location
    if not latitude or not longitude:
        try:
            response = requests.get(
                f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={GOOGLE_API_KEY}'
            )
            geo_data = response.json()
            if geo_data['status'] == 'OK':
                latitude = geo_data['results'][0]['geometry']['location']['lat']
                longitude = geo_data['results'][0]['geometry']['location']['lng']
            else:
                latitude = None
                longitude = None
        except Exception as e:
            print(f"Geocoding error: {e}")
            latitude = None
            longitude = None

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO reports (location, description, latitude, longitude) VALUES (?, ?, ?, ?)",
              (location, description, latitude, longitude))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Report added!', 'location': location, 'description': description})

# Fetch all reports
@app.route('/reports', methods=['GET'])
def get_reports():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, location, description, latitude, longitude, photo_path, status FROM reports")
    reports = [
        {
            'id': row[0],
            'location': row[1],
            'description': row[2],
            'latitude': row[3],
            'longitude': row[4],
            'photo_path': row[5],
            'status': row[6]
        } for row in c.fetchall()
    ]
    conn.close()
    return jsonify(reports)

# Clear selected reports
@app.route('/clear-reports', methods=['POST'])
def clear_reports():
    data = request.get_json()
    report_ids = data.get('report_ids', [])

    if not report_ids:
        return jsonify({'message': 'No reports selected to clear'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM reports WHERE id IN ({})".format(','.join('?' * len(report_ids))), report_ids)
    conn.commit()
    conn.close()
    return jsonify({'message': 'Selected reports cleared'})

# Update the status of a report
@app.route('/update-status', methods=['POST'])
def update_status():
    data = request.get_json()
    report_id = data.get('report_id')
    status = data.get('status')

    if not report_id or not status:
        return jsonify({'message': 'Report ID and status are required'}), 400

    if status not in ['Not Reported Yet', 'Reporting', 'In Process', 'Handled']:
        return jsonify({'message': 'Invalid status'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE reports SET status = ? WHERE id = ?", (status, report_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Status updated'})

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)