import re
import os
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import GoogleDriveLoader, OneDriveLoader, SharePointLoader
from loguru import logger

class ConnectorManager:
    @staticmethod
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
                return docs
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
