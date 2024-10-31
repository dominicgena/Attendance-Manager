from flask import Flask, request, redirect, abort
from google.oauth2 import service_account
from googleapiclient.discovery import build
import urllib.parse

app = Flask(__name__)

# Path to your credentials JSON file
SERVICE_ACCOUNT_FILE = 'data/attendanceproject-438417-58f04b8ae5f3.json'

# Authenticate with Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Access the Google Sheets API
service = build('sheets', 'v4', credentials=creds)
spreadsheet_id = 'sheet_id'

# Entry IDs for Google Form
FORM_BASE_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSfVhEi6WpK3lVU25_kxVWXA0339-LSk0Rn0jbmFvZX_Ovfr2g/viewform'
ENTRY_ID_NAME = 'entry.1287814510'
ENTRY_ID_DAY = 'entry.1000774895'
ENTRY_ID_START_TIME = 'entry.1379232146'
ENTRY_ID_END_TIME = 'entry.1137227360'

@app.route('/fill-form')
def fill_form():
    row = request.args.get('row')  # Get the row number from the URL parameter

    # Get data from the Google Sheet for the specified row
    range_name = f'Lessons!A{row}:F{row}'  # Fetch data for the specified row
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    # Check if the "Name" column (column A) is empty
    if not values or len(values[0]) == 0 or values[0][0].strip() == '':
        # If the "Name" is empty, return an error page
        return "404 - Please ensure you scanned the correct QR code.", 404

    # Extract values (Assuming columns A, C, E, F for Name, Day, Start Time, End Time)
    name = values[0][0] if len(values[0]) > 0 else ''
    day = values[0][1] if len(values[0]) > 1 else ''
    start_time = values[0][2] if len(values[0]) > 2 else ''
    end_time = values[0][3] if len(values[0]) > 3 else ''

    # Create the pre-filled Google Form URL
    params = {
        ENTRY_ID_NAME: name,
        ENTRY_ID_DAY: day,
        ENTRY_ID_START_TIME: start_time,
        ENTRY_ID_END_TIME: end_time
    }

    pre_filled_url = FORM_BASE_URL + '?' + urllib.parse.urlencode(params)

    # Redirect the user to the pre-filled Google Form
    return redirect(pre_filled_url)

if __name__ == '__main__':
    app.run(debug=True)
