from flask import Flask, request
import requests
import json

app = Flask(__name__)


SERVER_KEY = "794832032280"  

@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.get_json()
    location = data.get("location")
    description = data.get("description")

    # Notification payload
    notification = {
        "notification": {
            "title": "New Disaster Reported!",
            "body": f"{location}: {description}"
        },
        "to": "/topics/disasters"  # Send to all subscribed to "disasters"
    }

    headers = {
        "Authorization": f"key={SERVER_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://fcm.googleapis.com/fcm/send",
        headers=headers,
        data=json.dumps(notification)
    )
    return {"message": "Notification sent!", "status": response.status_code}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
