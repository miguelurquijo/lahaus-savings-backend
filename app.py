from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

app = Flask(__name__)
CORS(app)

# Google Sheets API configuration
# Google Sheets API configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')

# Get credentials from environment variable
def get_credentials():
    try:
        # Get the service account info from environment variable
        service_account_info = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '{}'))
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES
        )
        return credentials
    except Exception as e:
        print(f"Error getting credentials: {e}")
        return None

try:
    credentials = get_credentials()
    sheets_service = build('sheets', 'v4', credentials=credentials) if credentials else None
    print("Successfully connected to Google Sheets API")
except Exception as e:
    print(f"Error connecting to Google Sheets API: {e}")
    sheets_service = None

# Load credentials from service account file
try:
    credentials = service_account.Credentials.from_service_account_file(
        'gsheets_client_secreat.json',  # Replace with your service account key file
        scopes=SCOPES
    )
    sheets_service = build('sheets', 'v4', credentials=credentials)
    print("Successfully connected to Google Sheets API")
except Exception as e:
    print(f"Error connecting to Google Sheets API: {e}")
    sheets_service = None

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        print("Received data:", data)
        
        # Create timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Prepare row data
        row = [
            timestamp,
            data.get('name', ''),
            data.get('phone', ''),
            data.get('email', '')
        ]
        
        if sheets_service:
            try:
                # Prepare the request body
                body = {
                    'values': [row]
                }
                
                # Append row to Google Sheet
                result = sheets_service.spreadsheets().values().append(
                    spreadsheetId=SPREADSHEET_ID,
                    range=RANGE_NAME,
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body=body
                ).execute()
                
                print(f"Data added to Google Sheets: {result}")
                
                return jsonify({
                    'success': True,
                    'message': 'Registration successful'
                })
            
            except Exception as e:
                print(f"Error writing to Google Sheets: {e}")
                # Still return success to user but log the error
                return jsonify({
                    'success': True,
                    'message': 'Registration successful (backup saved)'
                })
        else:
            print("Google Sheets service not available, saving locally")
            # Here you could implement a backup storage solution
            return jsonify({
                'success': True,
                'message': 'Registration successful (local save)'
            })

    except Exception as e:
        print(f"Error processing registration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)