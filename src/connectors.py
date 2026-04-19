import os
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import GoogleDriveLoader, OneDriveLoader, SharePointLoader
from loguru import logger

class ConnectorManager:
    @staticmethod
    def load_from_gdrive(folder_id: str, service_account_path: str = None, credentials_path: str = None, token_path: str = "token.json") -> List[Document]:
        """Load documents from a Google Drive folder."""
        logger.info(f"Loading from GDrive folder: {folder_id}")
        try:
            kwargs = {
                "folder_id": folder_id,
                "recursive": False
            }
            if service_account_path and os.path.exists(service_account_path):
                kwargs["service_account_key"] = service_account_path
            elif credentials_path and os.path.exists(credentials_path):
                kwargs["credentials_path"] = credentials_path
                kwargs["token_path"] = token_path

            loader = GoogleDriveLoader(**kwargs)
            return loader.load()
        except Exception as e:
            logger.error(f"GDrive Load Error: {e}")
            raise

    @staticmethod
    def load_from_onedrive(drive_id: str, folder_path: str = None) -> List[Document]:
        """Load documents from OneDrive."""
        logger.info(f"Loading from OneDrive: {drive_id}")
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
    def load_from_sharepoint(site_id: str, document_library_id: str = None) -> List[Document]:
        """Load documents from SharePoint."""
        logger.info(f"Loading from SharePoint site: {site_id}")
        try:
            loader = SharePointLoader(
                site_id=site_id,
                document_library_id=document_library_id
            )
            return loader.load()
        except Exception as e:
            logger.error(f"SharePoint Load Error: {e}")
            raise
