import os
import json
from typing import Optional

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class AuthCodeInvalidError(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class NoCredentialFile(Exception):
    pass


class GoogleAuth:

    OAUTH_SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]
    REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"

    def __init__(self, CLIENT_ID: str, CLIENT_SECRET: str):
        self.client_config = {
            "installed": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [self.REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

        self.flow = Flow.from_client_config(
            self.client_config,
            scopes=self.OAUTH_SCOPE,
            redirect_uri=self.REDIRECT_URI,
        )

        self.credentials: Optional[Credentials] = None

    # ✅ Step 1: Get auth URL
    def GetAuthUrl(self) -> str:
        auth_url, _ = self.flow.authorization_url(
            access_type="offline",
            prompt="consent"
        )
        return auth_url

    # ✅ Step 2: Exchange code
    def Auth(self, code: str) -> None:
        try:
            self.flow.fetch_token(code=code)
            self.credentials = self.flow.credentials
        except Exception as e:
            raise AuthCodeInvalidError(e)

    # ✅ Build YouTube client
    def authorize(self):
        try:
            if not self.credentials:
                raise InvalidCredentials("No credentials available")

            # refresh token if expired
            if self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())

            return build(
                self.API_SERVICE_NAME,
                self.API_VERSION,
                credentials=self.credentials,
            )

        except Exception as e:
            raise e

    # ✅ Load credentials
    def LoadCredentialsFile(self, cred_file: str) -> None:
        if not os.path.isfile(cred_file):
            raise NoCredentialFile(f"{cred_file} not found")

        with open(cred_file, "r") as f:
            data = json.load(f)

        self.credentials = Credentials.from_authorized_user_info(data)

    # ✅ Save credentials
    def SaveCredentialsFile(self, cred_file: str) -> None:
        if not self.credentials:
            raise InvalidCredentials("No credentials to save")

        with open(cred_file, "w") as f:
            f.write(self.credentials.to_json())
