import os
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import GoogleDriveLoader, OneDriveLoader, SharePointLoader
from loguru import logger
from google_auth_oauthlib.flow import InstalledAppFlow
from O365 import Account

class ConnectorManager:
    # --- Google Drive Helpers ---
    @staticmethod
    def get_gdrive_auth_url(credentials_path: str) -> str:
        """Generate Google Auth URL."""
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        # We use a static redirect URI for the 'copy-paste' flow
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url

    @staticmethod
    def exchange_gdrive_code(credentials_path: str, code: str, token_path: str = "token.json"):
        """Exchange code for token and save it."""
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        flow.fetch_token(code=code)
        with open(token_path, 'w') as f:
            f.write(flow.credentials.to_json())
        return True

    # --- Microsoft Helpers ---
    @staticmethod
    def get_ms_auth_url(client_id: str, client_secret: str) -> str:
        """Generate Microsoft Auth URL."""
        account = Account((client_id, client_secret))
        scopes = ['offline_access', 'Files.Read.All']
        url, _ = account.con.get_authorization_url(requested_scopes=scopes)
        return url

    @staticmethod
    def exchange_ms_code(client_id: str, client_secret: str, code_url: str):
        """Exchange redirect URL/code for token."""
        account = Account((client_id, client_secret))
        if account.authenticate(url=code_url):
            return True
        return False

    @staticmethod
    def load_from_gdrive(folder_id: str, service_account_path: str = None, token_path: str = "token.json") -> List[Document]:
        """Load documents from a Google Drive folder."""
        logger.info(f"Loading from GDrive folder: {folder_id}")
        try:
            kwargs = {
                "folder_id": folder_id,
                "recursive": False,
                "token_path": token_path
            }
            if service_account_path and os.path.exists(service_account_path):
                kwargs["service_account_key"] = service_account_path

            loader = GoogleDriveLoader(**kwargs)
            return loader.load()
        except Exception as e:
            logger.error(f"GDrive Load Error: {e}")
            raise

    @staticmethod
    def load_from_onedrive(drive_id: str, folder_path: str = None, client_id: str = None, client_secret: str = None) -> List[Document]:
        """Load documents from OneDrive."""
        logger.info(f"Loading from OneDrive: {drive_id}")
        if client_id:
            os.environ["O365_CLIENT_ID"] = client_id
        if client_secret:
            os.environ["O365_CLIENT_SECRET"] = client_secret
        try:
            loader = OneDriveLoader(
                drive_id=drive_id,
                folder_path=folder_path,
                object_name="one_drive"
            )
            return loader.load()
        except Exception as e:
            logger.error(f"OneDrive Load Error: {e}")
            raise

    @staticmethod
    def load_from_sharepoint(site_id: str, document_library_id: str = None, client_id: str = None, client_secret: str = None) -> List[Document]:
        """Load documents from SharePoint."""
        logger.info(f"Loading from SharePoint site: {site_id}")
        if client_id:
            os.environ["O365_CLIENT_ID"] = client_id
        if client_secret:
            os.environ["O365_CLIENT_SECRET"] = client_secret
        try:
            loader = SharePointLoader(
                site_id=site_id,
                document_library_id=document_library_id
            )
            return loader.load()
        except Exception as e:
            logger.error(f"SharePoint Load Error: {e}")
            raise
