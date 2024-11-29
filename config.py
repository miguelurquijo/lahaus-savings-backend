# Google Sheets Configuration
SPREADSHEET_CONFIG = {
    'SCOPES': ['https://www.googleapis.com/auth/spreadsheets'],
    'SPREADSHEET_ID': '1x4zRUOrhbi6pLYehE1Bu9Iw33tdkZjfg21amBFU5nqM',  # Replace with your Google Sheet ID
    'RANGE_NAME': 'raw_registers!A:E',
    'SHEET_HEADERS': [
        'Timestamp',
        'Name',
        'Phone',
        'Email'
    ]
}

# Flask Configuration
FLASK_CONFIG = {
    'DEBUG': True,
    'HOST': '0.0.0.0',
    'PORT': 5000
}