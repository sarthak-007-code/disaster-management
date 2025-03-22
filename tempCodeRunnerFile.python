from flask import Flask, request, jsonify

app = Flask(__name__)

# Store reports in memory (simple list)
reports = []

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/report', methods=['POST'])
def report_disaster():
    data = request.get_json()
    location = data['location']
    description = data['description']
    reports.append({'location': location, 'description': description})
    return jsonify({'message': 'Report added!', 'location': location, 'description': description})

if __name__ == '__main__':
    app.run(debug=True)