import os
import requests
from flask import Flask, request, jsonify, make_response, send_from_directory
import sqlite3

app = Flask(__name__)

# Google API key (store in environment variables in production)
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Ensure the uploads folder exists
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

# Initialize the database on startup
init_db()

# Homepage with role selector
@app.route('/')
def home():
    # Clear the role cookie
    resp = make_response(app.send_static_file('index.html'))
    resp.set_cookie('role', '', expires=0)
    return resp

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
    # Since we're handling file uploads, we can't use request.get_json()
    location = request.form.get('location')
    description = request.form.get('description')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    photo = request.files.get('photo')

    # Convert latitude and longitude to float (or None)
    latitude = float(latitude) if latitude and latitude != 'null' else None
    longitude = float(longitude) if longitude and longitude != 'null' else None

    # If latitude and longitude are not provided, geocode the location
    if not latitude or not longitude:
        try:
            response = requests.get(
                f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={GOOGLE_API_KEY}'
            )
            geo_data = response.json()
            print(f"Geocoding response for '{location}': {geo_data}")  # Debug log
            if geo_data['status'] == 'OK':
                latitude = geo_data['results'][0]['geometry']['location']['lat']
                longitude = geo_data['results'][0]['geometry']['location']['lng']
            else:
                print(f"Geocoding failed for '{location}': {geo_data['status']}")
                # Fallback coordinates for common locations
                location_lower = location.lower()
                if "pune" in location_lower:
                    latitude = 18.5204
                    longitude = 73.8567
                elif "mumbai" in location_lower:
                    latitude = 19.0760
                    longitude = 72.8777
                else:
                    latitude = None
                    longitude = None
        except Exception as e:
            print(f"Geocoding error for '{location}': {e}")
            # Fallback coordinates for common locations
            location_lower = location.lower()
            if "pune" in location_lower:
                latitude = 18.5204
                longitude = 73.8567
            elif "mumbai" in location_lower:
                latitude = 19.0760
                longitude = 72.8777
            else:
                latitude = None
                longitude = None

    # Handle photo upload
    photo_path = None
    if photo:
        # Validate file type (only allow images)
        if not photo.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return jsonify({'message': 'Only PNG, JPG, and JPEG files are allowed'}), 400
        # Validate file size (e.g., max 5MB)
        photo.seek(0, os.SEEK_END)
        file_size = photo.tell()
        if file_size > 5 * 1024 * 1024:  # 5MB limit
            return jsonify({'message': 'File size exceeds 5MB limit'}), 400
        photo.seek(0)  # Reset file pointer

        # Save the file
        filename = f"{os.urandom(16).hex()}_{photo.filename}"
        photo_path = os.path.join(UPLOAD_FOLDER, filename)
        photo.save(photo_path)
        photo_path = f"/{photo_path}"  # Store as URL path (e.g., /static/uploads/...)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO reports (location, description, latitude, longitude, photo_path, status) VALUES (?, ?, ?, ?, ?, ?)",
              (location, description, latitude, longitude, photo_path, 'Not Reported Yet'))
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