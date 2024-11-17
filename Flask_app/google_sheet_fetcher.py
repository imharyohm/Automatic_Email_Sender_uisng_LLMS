import gspread
from google.oauth2.service_account import Credentials

SHEET_SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CLIENT_SECRETS_FILE_SHEET="client_key.json"

def fetch_google_sheet_data(sheet_url):
    credentials= Credentials.from_service_account_file(CLIENT_SECRETS_FILE_SHEET,scopes=SHEET_SCOPES)
    client = gspread.authorize(credentials)
    sheet_id = sheet_url.split("/")[5]
    sheet = client.open_by_key(sheet_id).sheet1
    values = sheet.get_all_records()
    if not values:
        print("Data not found")
        return []
    return values