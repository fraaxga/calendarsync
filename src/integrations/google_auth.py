import json
import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

log = logging.getLogger(__name__)

class GoogleAuth:
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, config_path: str = "src/config"):
        self.config_dir = Path(config_path)
        self.token_file = self.config_dir / 'token.json'  
        self.creds_file = self.config_dir / 'credentials.json'
        
        self._creds = None

    def _load_stored_credentials(self) -> Credentials | None:
        if not self.token_file.exists():
            return None
        try:
            return Credentials.from_authorized_user_file(str(self.token_file), self.SCOPES)
        except Exception:
            log.exception("Stored token is invalid or corrupted")
            return None

    def _refresh_or_auth(self) -> Credentials:
        creds = self._load_stored_credentials()
        
        if creds and creds.valid:
            return creds
            
        if creds and creds.expired and creds.refresh_token:
            try:
                log.info("Refreshing expired Google access token...")
                creds.refresh(Request())
                self._save_credentials(creds)
                return creds
            except Exception:
                log.warning("Refresh token failed, starting new flow")

        return self._run_new_auth_flow()

    def _run_new_auth_flow(self) -> Credentials:
        if not self.creds_file.exists():
            log.error("Credentials file not found at %s", self.creds_file)
            raise FileNotFoundError(f"Missing {self.creds_file}")

        flow = InstalledAppFlow.from_client_secrets_file(str(self.creds_file), self.SCOPES)
        creds = flow.run_local_server(port=0, prompt='consent')
        
        self._save_credentials(creds)
        return creds

    def _save_credentials(self, creds: Credentials):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.token_file, 'w', encoding='utf-8') as f:
            f.write(creds.to_json())
        log.info("Access token successfully saved to %s", self.token_file)

    def get_service(self):
        creds = self._refresh_or_auth()
        return build('calendar', 'v3', credentials=creds, static_discovery=False)
    