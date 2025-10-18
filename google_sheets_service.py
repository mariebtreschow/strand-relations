import os
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

class GoogleSheetsService:
    """Service class for interacting with Google Sheets API"""
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API using Service Account"""
        try:
            # Try Service Account authentication first
            from google.oauth2 import service_account
            
            if os.path.exists(self.credentials_file):
                creds = service_account.Credentials.from_service_account_file(
                    self.credentials_file, scopes=self.SCOPES)
                self.service = build('sheets', 'v4', credentials=creds)
                print("✅ Authenticated using Service Account")
                return
        except Exception as e:
            print(f"⚠️ Service Account authentication failed: {e}")
        
        # Fallback to OAuth 2.0 if Service Account fails
        creds = None
        
        # The file token.json stores the user's access and refresh tokens.
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file '{self.credentials_file}' not found. "
                        "Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('sheets', 'v4', credentials=creds)
        print("✅ Authenticated using OAuth 2.0")
    
    def get_sheet_data(self, spreadsheet_id, range_name):
        """
        Get data from a Google Sheet
        
        Args:
            spreadsheet_id: The ID of the Google Sheet
            range_name: The range to read (e.g., 'Sheet1!A1:Z100')
        
        Returns:
            pandas.DataFrame: The sheet data as a DataFrame
        """
        try:
            # Call the Sheets API
            sheet = self.service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print('No data found.')
                return pd.DataFrame()
            
            # Convert to DataFrame
            # First row as headers
            headers = values[0]
            data = values[1:] if len(values) > 1 else []
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=headers)
            
            return df
            
        except HttpError as err:
            print(f'An error occurred: {err}')
            return pd.DataFrame()
    
    def get_sheet_names(self, spreadsheet_id):
        """
        Get all sheet names from a Google Spreadsheet
        
        Args:
            spreadsheet_id: The ID of the Google Sheet
        
        Returns:
            list: List of sheet names
        """
        try:
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheets = sheet_metadata.get('sheets', [])
            return [sheet['properties']['title'] for sheet in sheets]
            
        except HttpError as err:
            print(f'An error occurred: {err}')
            return []
