Crowdsourced Disaster Relief Platform


 OVERVIEW - 

The Crowdsourced Disaster Relief Platform is a web application designed to facilitate disaster reporting and coordination. It allows users to report disasters with details such as location, description, and photos, while volunteers can view these reports on a map, update their status, and coordinate relief efforts. The app is built using Flask (Python) for the backend, SQLite for the database, and HTML/JavaScript with the Google Maps API for the frontend. It is deployed on Render for easy access.

 FEATURES - 

   1. Role-Based Access:
        Users: Can report disasters by providing a location (manually entered     or via live location), a description, and an optional photo.
        Volunteers: Can view all reports on a map, update the status of reports (e.g., "Not Reported Yet", "Reporting", "In Process", "Handled"), and clear      selected reports.
   2.Geocoding and Mapping:
        Uses the Google Geocoding API to convert manually entered locations (e.g., "Pune") into latitude and longitude coordinates.
        Displays reports as markers on a Google Map in the volunteer interface.
        Supports live location reporting using the browser’s Geolocation API.
    3.Photo Uploads:
        Users can upload photos (PNG, JPG, JPEG) with a maximum size of 5MB when reporting a disaster.
        Photos are displayed in the volunteer interface alongside the report details.
    4. Persistent Storage:
        Stores reports in a SQLite database (reports.db) with fields for location, description, latitude, longitude, photo path, and status.
   5. Default Status:
        New reports are automatically set to "Not Reported Yet" status.
    Navigation:
        Includes a "Back to Home" button to return to the role selection page, clearing the role cookie for easy switching between user and volunteer modes.

Project Structure

crowdsourced-disaster-relief/
│
├── app.py                  # Flask backend application
├── reports.db              # SQLite database (created on first run)
├── static/                 # Static files (HTML, CSS, JavaScript)
│   ├── index.html          # Homepage with role selection
│   ├── report.html         # User interface for reporting disasters
│   ├── volunteer.html      # Volunteer interface for viewing reports
│   └── uploads/            # Folder for uploaded photos
├── requirements.txt        # Python dependencies
└── README.md               # This file
Prerequisites

To run this project locally, you’ll need the following:

    Python 3.8+: Install from python.org.
    Git: To clone the repository.
    Google API Key: For geocoding and mapping features (Geocoding API, Maps JavaScript API, and optionally Geolocation API).
    Render Account: For deployment (optional).

Setup Instructions
1. Clone the Repository

git clone https://github.com/sarthak-007-code/disaster-management
cd <disaster-management>

2. Set Up a Virtual Environment

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies

pip install -r requirements.txt

The requirements.txt should include:
text
flask==2.0.1
requests==2.28.1

If you don’t have a requirements.txt, create one with the above content.
4. Set Up the Google API Key

    Go to the Google Cloud Console.
    Create a new project or select an existing one.
    Enable the following APIs:
        Geocoding API
        Maps JavaScript API
        Geolocation API (optional, for live location)
    Create an API key under "APIs & Services" > "Credentials."
    Configure the API key:
        API Restrictions: Restrict to the above APIs.
        Application Restrictions: Set to "HTTP referrers (web sites)" and add:
            *.onrender.com/* (for Render deployment)
            localhost:*/* (for local testing)
    Set the API key as an environment variable:
        
    On macOS/Linux:
export GOOGLE_API_KEY=<your-api-key>
On Windows (Command Prompt):

        set GOOGLE_API_KEY=<your-api-key>

5. Run the Application Locally

python app.py

    Open your browser and go to http://localhost:5000.
    You should see the homepage with a role selection dropdown ("I am a User" or "I am a Volunteer").

Usage
As a User

    Select "I am a User" on the homepage and click "Proceed."
    You’ll be taken to the "Report a Disaster" page.
    Fill in the details:
        Location: Enter a location manually (e.g., "Pune") or click "Get My Location" to use your current location.
        Description: Describe the disaster.
        Photo: Upload an optional photo (PNG, JPG, JPEG, max 5MB).
    Click "Submit Report."
    You’ll see a confirmation message ("Report added!").

As a Volunteer

    Select "I am a Volunteer" on the homepage and click "Proceed."
    You’ll be taken to the Volunteer Dashboard.
    View all reports on a Google Map with markers.
    For each report, you can:
        See the location, description, status, and photo (if uploaded).
        Update the status ("Not Reported Yet", "Reporting", "In Process", "Handled").
        Select reports using checkboxes and click "Clear Selected Reports" to delete them.
    Click "Refresh Reports" to update the list and map.
    Click "Back to Home" to return to the role selection page.

Deployment on Render
1. Push to GitHub

Ensure your repository is pushed to GitHub:
bash
git add .
git commit -m "Initial commit"
git push origin main  # Replace 'main' with your branch name (e.g., 'sarthak')
2. Create a Render Service

    Go to Render and sign in.
    Click "New" > "Web Service."
    Connect your GitHub repository and select the branch (e.g., sarthak).
    Configure the service:
        Name: disaster-management
        Environment: Python 3
        Build Command: pip install -r requirements.txt
        Start Command: python app.py
    Add the environment variable:
        Key: GOOGLE_API_KEY
        Value: <your-api-key>
    Click "Create Web Service."
    Once deployed, Render will provide a URL (e.g., https://disaster-management.onrender.com).

3. Test the Deployed App

    Open the Render URL in your browser.
    Test the app as a user and volunteer to ensure everything works as expected.

Known Issues and Limitations

    Geocoding Failures: If the Google Geocoding API fails (e.g., due to rate limits or API key issues), manually entered locations may not show as markers on the map. Fallback coordinates are used for "Pune" and "Mumbai" to mitigate this.
    Persistent Storage: The SQLite database (reports.db) and uploaded photos are stored on the local filesystem, which may not persist on Render due to its ephemeral filesystem. Consider using a cloud database (e.g., PostgreSQL) and cloud storage (e.g., AWS S3) for production.
    Rate Limits: The Google Maps APIs have rate limits (e.g., 300 geocoding requests per minute in the free tier). Heavy usage may require a paid plan.

Future Improvements

    Google Places Autocomplete: Add autocomplete to the location input in report.html to improve location accuracy and reduce geocoding failures.
    Marker Clustering: Implement marker clustering in volunteer.html to handle overlapping markers on the map.
    Cloud Storage: Use a cloud database (e.g., PostgreSQL) and cloud storage (e.g., AWS S3) for persistent storage.
    User Authentication: Add login functionality to secure user and volunteer roles.
    UI Enhancements: Use a CSS framework (e.g., Bootstrap) to improve the app’s appearance.
