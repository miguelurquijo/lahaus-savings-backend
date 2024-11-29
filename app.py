from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json
from datetime import datetime

app = Flask(__name__)

# Configure CORS to allow requests from specific origins
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Google Sheets API configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')  # Make sure this is set in Heroku

# Load credentials from the environment variable
try:
    # Read the service account credentials from the environment variable
    google_credentials = os.environ.get('GOOGLE_CREDENTIALS')
    if not google_credentials:
        raise Exception("GOOGLE_CREDENTIALS environment variable is not set.")
    
    credentials_info = json.loads(google_credentials)
    credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
    sheets_service = build('sheets', 'v4', credentials=credentials)
    print("Successfully connected to Google Sheets API")
except Exception as e:
    print(f"Error connecting to Google Sheets API: {e}")
    sheets_service = None


@app.route('/api/register', methods=['POST'])
def register():
    """
    Handles user registration by receiving POST data and saving it to Google Sheets.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid JSON input'}), 400

        print("Received data:", data)

        # Create timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Prepare the row to add to Google Sheets
        row = [
            timestamp,
            data.get('name', ''),
            data.get('phone', ''),
            data.get('email', '')
        ]

        if sheets_service:
            try:
                # Prepare the request body for Google Sheets
                body = {'values': [row]}
                
                # Append the row to the Google Sheet
                result = sheets_service.spreadsheets().values().append(
                    spreadsheetId=SPREADSHEET_ID,
                    range="raw_registers!A:D",  # Adjust the range based on your sheet
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body=body
                ).execute()
                
                print(f"Data added to Google Sheets: {result}")
                
                return jsonify({'success': True, 'message': 'Registration successful'})
            except Exception as e:
                print(f"Error writing to Google Sheets: {e}")
                return jsonify({'success': False, 'message': 'Failed to save data to Google Sheets.'}), 500
        else:
            print("Google Sheets service not available.")
            return jsonify({'success': False, 'message': 'Google Sheets service is unavailable.'}), 503

    except Exception as e:
        print(f"Error processing registration: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Use the PORT environment variable (required for Heroku)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)