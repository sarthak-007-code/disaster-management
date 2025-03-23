import os
from flask import Flask, request, jsonify, make_response, send_from_directory
import sqlite3

app = Flask(__name__)

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
            status TEXT DEFAULT 'Reported'
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
        return app.send_static_file('index.html')  # Redirect to homepage if not a user
    return app.send_static_file('report.html')

# Volunteer interface for viewing disasters
@app.route('/volunteer-page')
def volunteer_page():
    role = request.cookies.get('role')
    if role != 'volunteer':
        return app.send_static_file('index.html')  # Redirect to homepage if not a volunteer
    return app.send_static_file('volunteer.html')

# Existing endpoint to submit a report
@app.route('/report', methods=['POST'])
def report_disaster():
    data = request.get_json()
    location = data['location']
    description = data['description']

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO reports (location, description) VALUES (?, ?)", (location, description))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Report added!', 'location': location, 'description': description})

# Existing endpoint to fetch all reports
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

# Existing endpoint to clear reports
@app.route('/clear-reports', methods=['POST'])
def clear_reports():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM reports")
    conn.commit()
    conn.close()
    return jsonify({'message': 'Reports cleared'})

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # For local testing only