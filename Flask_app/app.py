from flask import Flask, redirect, session, request, render_template, url_for, jsonify
import csv
import io
import json
import os
import requests  # For API requests to Django

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_sheet_fetcher import fetch_google_sheet_data
from mainapp.models import EmailTracking  # Adjust the import path as needed
from datetime import datetime
app = Flask(__name__)


CLIENT_SECRETS_FILE = "C:\\Users\\KIIT\\Desktop\\Email Sender Project\\Automatic_Email_Sender\\Flask_app\\client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

@app.route("/")
def index():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit_form():
    sheet_url = request.form.get("sheet_url")
    email_content = request.form.get("email_content")
    csv_file = request.files.get("csv_file")

    data_rows = []
    if sheet_url:
        data_rows = fetch_google_sheet_data(sheet_url)
        print("GOOOOOT URL")
    elif csv_file:
        data_rows_response = upload_csv(csv_file)
        if isinstance(data_rows_response, tuple) and data_rows_response[1] == 400:
            return data_rows_response
        data_rows = data_rows_response

    # Collect additional data
        schedule_time = int(request.form.get("schedule_time"))
        # email_list = []
        # for row in data_rows:
        #     email = row.get("email")
        #     if email:
        #         email_list.append(email.split())  # Emails from the user form

        # POST request to Django API
        response = requests.post("http://localhost:8000/api/schedule_emails/", json={
            "email_content":email_content,
            "schedule_time": schedule_time,
            "data_rows": data_rows  # Include recipient-specific data for personalization
        })
        print(f"Request Payload: {json.dumps({'email_content':email_content, 'schedule_time': schedule_time, 'data_rows': data_rows}, indent=4)}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")
        if response.status_code == 200:
            return jsonify({"message": "Scheduling initiated."})
        else:
            return jsonify({"error": "Failed to schedule emails."}), 400
    return redirect(url_for("analytics"))

@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = "http://localhost:5000/oauth2callback"
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = "http://localhost:5000/oauth2callback"
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    session['credentials'] = json.dumps(credentials_to_dict(credentials))
    return redirect(url_for('index'))

def credentials_to_dict(credentials):
    credentials_dict = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }
    app.config['CREDENTIALS'] = json.dumps(credentials_dict)
    return credentials_dict

def upload_csv(csv_file):
    if csv_file.filename == "":
        return "No file selected", 400

    if csv_file and csv_file.filename.endswith(".csv"):
        stream = io.StringIO(csv_file.stream.read().decode("UTF-8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        expected_columns = {"Company Name", "Location", "Email", "Products"}
        if not expected_columns.issubset(csv_reader.fieldnames):
            return "CSV file missing required columns", 400

        data = [row for row in csv_reader]
        return data
    else:
        return "Invalid file format", 400

email_analytics_data = {
    "total_emails": 500,
    "emails_sent": 450,
    "emails_pending": 30,
    "emails_scheduled": 10,
    "emails_failed": 10,
}

# Route to render the analytics page
@app.route('/analytics')
def analytics_page():
    return render_template('email_analytics.html')

# API endpoint to provide analytics data
@app.route('/api/email-analytics')
def email_analytics():
    return jsonify(email_analytics_data)

@app.route('/email-events', methods=['POST'])
def email_events():
    """Webhook to handle email events from SendGrid."""
    events = request.json
    for event in events:
        email = event.get('email')
        status = event.get('event')  # "delivered", "open", "bounce", etc.
        timestamp = datetime.now()

        # Save the event data to the database
        EmailTracking.objects.create(email=email, status=status, timestamp=timestamp)

        print(f"Email: {email}, Status: {status}, Timestamp: {timestamp}")

    return jsonify({"message": "Events received"}), 200


if __name__ == "__main__":
    app.secret_key = 'your_secret_key'
    app.run(port=6380, debug=True)
