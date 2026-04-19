import re
import os
import threading
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import GoogleDriveLoader, OneDriveLoader, SharePointLoader
from loguru import logger
from google_auth_oauthlib.flow import InstalledAppFlow
from src.utils import extract_id_from_url
from O365 import Account

# Global lock for thread-safe environment variable modification (for Microsoft connectors)
ms_env_lock = threading.Lock()

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
        # Note: 'oob' is deprecated but often the only choice for simple CLI/Streamlit flows
        # without a registered redirect web server.
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
 fix-gdrive-auth-timeout-17440176441863980092
    def load_from_gdrive(input_id: str, service_account_path: str = None, token_path: str = "token.json") -> List[Document]:
        """Load documents from a Google Drive folder or file."""
        actual_id = extract_id_from_url(input_id)
        logger.info(f"Loading from GDrive (Input: {input_id}, Extracted ID: {actual_id})")

        try:
            kwargs = {
                "recursive": False,
                "token_path": token_path
            }

            # Determine if it's a folder or file by looking at the URL context
            if "/d/" in input_id:
                kwargs["file_ids"] = [actual_id]
            else:
                kwargs["folder_id"] = actual_id

            if service_account_path and os.path.exists(service_account_path):
                kwargs["service_account_key"] = service_account_path

            loader = GoogleDriveLoader(**kwargs)
            return loader.load()

    def extract_id_from_url(url_or_id: str) -> str:
        """Extract Google Drive ID from a URL or return the ID if it's already one."""
        if not url_or_id:
            return ""

        # Handle various Google Drive URL patterns
        patterns = [
            r"/d/([a-zA-Z0-9_-]+)",          # Document/File URL
            r"id=([a-zA-Z0-9_-]+)",          # id= parameter
            r"folders/([a-zA-Z0-9_-]+)",     # Folders URL
            r"open\?id=([a-zA-Z0-9_-]+)"     # Open link
        ]

        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)

        return url_or_id.strip()

    @staticmethod
    def load_from_gdrive(input_id: str, service_account_path: str = None) -> List[Document]:
        """Load documents from a Google Drive folder or individual file."""
        g_id = ConnectorManager.extract_id_from_url(input_id)
        if not g_id:
            raise ValueError("Invalid Google Drive Link or ID.")

        logger.info(f"Loading from GDrive ID: {g_id}")

        loader_kwargs = {
            "service_account_key": service_account_path if service_account_path and os.path.exists(service_account_path) else None,
            "recursive": False
        }
        loader_kwargs = {k: v for k, v in loader_kwargs.items() if v is not None}

        # Strategy 1: Load as a folder
        try:
            logger.info("Strategy 1: Attempting to load as folder...")
            loader = GoogleDriveLoader(folder_id=g_id, **loader_kwargs)
            docs = loader.load()
            if docs:
                return docs>>>>>>> main
        except Exception as e:
            logger.debug(f"Strategy 1 (Folder) failed: {e}")

        # Strategy 2: Load as a Document ID (for Google Docs)
        try:
            logger.info("Strategy 2: Attempting to load as Document ID...")
            loader = GoogleDriveLoader(document_ids=[g_id], **loader_kwargs)
            docs = loader.load()
            if docs:
                return docs
        except Exception as e:
            logger.debug(f"Strategy 2 (Doc ID) failed: {e}")

        # Strategy 3: Load as a File ID (for binary files)
        try:
            logger.info("Strategy 3: Attempting to load as File ID...")
            loader = GoogleDriveLoader(file_ids=[g_id], **loader_kwargs)
            docs = loader.load()
            if docs:
                return docs
        except Exception as e:
            logger.debug(f"Strategy 3 (File ID) failed: {e}")

        return []

    @staticmethod
    def load_from_onedrive(drive_id: str, folder_path: str = None, client_id: str = None, client_secret: str = None) -> List[Document]:
        """Load documents from OneDrive."""
        logger.info(f"Loading from OneDrive: {drive_id}")

        with ms_env_lock:
            # Temporarily set environment variables for the loader
            old_id = os.environ.get("O365_CLIENT_ID")
            old_secret = os.environ.get("O365_CLIENT_SECRET")

            if client_id: os.environ["O365_CLIENT_ID"] = client_id
            if client_secret: os.environ["O365_CLIENT_SECRET"] = client_secret

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
            finally:
                # Restore original environment
                if old_id: os.environ["O365_CLIENT_ID"] = old_id
                elif "O365_CLIENT_ID" in os.environ: del os.environ["O365_CLIENT_ID"]

                if old_secret: os.environ["O365_CLIENT_SECRET"] = old_secret
                elif "O365_CLIENT_SECRET" in os.environ: del os.environ["O365_CLIENT_SECRET"]

    @staticmethod
    def load_from_sharepoint(site_id: str, document_library_id: str = None, client_id: str = None, client_secret: str = None) -> List[Document]:
        """Load documents from SharePoint."""
        logger.info(f"Loading from SharePoint site: {site_id}")

        with ms_env_lock:
            old_id = os.environ.get("O365_CLIENT_ID")
            old_secret = os.environ.get("O365_CLIENT_SECRET")

            if client_id: os.environ["O365_CLIENT_ID"] = client_id
            if client_secret: os.environ["O365_CLIENT_SECRET"] = client_secret

            try:
                loader = SharePointLoader(
                    site_id=site_id,
                    document_library_id=document_library_id
                )
                return loader.load()
            except Exception as e:
                logger.error(f"SharePoint Load Error: {e}")
                raise
            finally:
                if old_id: os.environ["O365_CLIENT_ID"] = old_id
                elif "O365_CLIENT_ID" in os.environ: del os.environ["O365_CLIENT_ID"]

                if old_secret: os.environ["O365_CLIENT_SECRET"] = old_secret
                elif "O365_CLIENT_SECRET" in os.environ: del os.environ["O365_CLIENT_SECRET"]
