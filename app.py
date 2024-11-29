from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Google Sheets API configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    """Create and return Google Sheets service object"""
    try:
        # Get credentials from environment variable
        credentials_json = os.getenv('GOOGLE_CREDENTIALS')
        if not credentials_json:
            raise ValueError("GOOGLE_CREDENTIALS environment variable not set")
        
        credentials_info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, 
            scopes=SCOPES
        )
        
        return build('sheets', 'v4', credentials=credentials)
    except Exception as e:
        print(f"Error creating sheets service: {e}")
        return None

@app.route('/api/register', methods=['POST'])
def register():
    """Handle user registration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid JSON input'}), 400

        # Get spreadsheet ID from environment
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        if not spreadsheet_id:
            return jsonify({'success': False, 'message': 'Spreadsheet ID not configured'}), 500

        # Create sheets service
        service = get_sheets_service()
        if not service:
            return jsonify({'success': False, 'message': 'Could not connect to Google Sheets'}), 503

        # Prepare row data
        row = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data.get('name', ''),
            data.get('phone', ''),
            data.get('email', '')
        ]

        # Append to sheet
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='raw_registers!A:D',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [row]}
        ).execute()

        return jsonify({'success': True, 'message': 'Registration successful'})

    except Exception as e:
        print(f"Error in registration: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)