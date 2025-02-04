import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd

# Define the Google Sheets API scope (read-only access)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Google Sheets ID from the URL
SHEET_ID = "1XOPTvTDs5q9szcdBQbHjT3dQYc6sGbqZx17LpliQtg8"
RANGE = "'Form responses 1'!A1:Z1000"  # Modify as needed

def authenticate():
    """Authenticate the user using OAuth 2.0 and token.json"""
    creds = None

    # Load credentials from token.json if it exists
    if os.path.exists("../token.json"):
        creds = Credentials.from_authorized_user_file("../token.json", SCOPES)

    # Refresh or create new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the updated credentials
        with open("../token.json", "w") as token:
            token.write(creds.to_json())

    return creds

def read_google_sheet():
    """Reads data from the Google Sheet and prints it as a DataFrame"""
    creds = authenticate()
    service = build("sheets", "v4", credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE).execute()
    values = result.get("values", [])

    if not values:
        print("No data found in the sheet.")
        return

    # Convert to DataFrame for better readability (optional)
    df = pd.DataFrame(values)
    colnames = ['course', 'student_id', 'original_group', 'new_group', 'accept_swap_teammate', 'swap_teammate_id']
    # remove first column from df
    df = df.iloc[1:, 1:]
    # set column names
    df.columns = colnames
    # write to swappers.csv 
    df.to_csv('swappers.csv', index=False)
    print("Data written to swappers.csv")
if __name__ == "__main__":
    read_google_sheet()
