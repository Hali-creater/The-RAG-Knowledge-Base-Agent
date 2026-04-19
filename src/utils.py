import os
import hashlib
import nltk

def download_nltk_data():
    """Download required NLTK data for unstructured loaders."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger')
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab')
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger_eng')
    except LookupError:
        nltk.download('averaged_perceptron_tagger_eng')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import re

def extract_id_from_url(url: str) -> str:
    """Extract Folder or File ID from a GDrive URL."""
    # Folder ID: .../folders/ID
    folder_match = re.search(r'folders/([a-zA-Z0-9_-]+)', url)
    if folder_match:
        return folder_match.group(1)

    # File/Doc ID: .../d/ID/...
    file_match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if file_match:
        return file_match.group(1)

    # Query param: ...?id=ID
    query_match = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', url)
    if query_match:
        return query_match.group(1)

    return url # Return as-is if no match (assume it's already an ID)

def get_file_hash(filepath):
    """Generate SHA-256 hash of file content for deduplication."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        # Read in 64k chunks
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def ensure_dirs():
    dirs = ['data/documents', 'data/chroma_db', 'uploads', 'logs']
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
    download_nltk_data()

ROLE_PERMISSIONS = {
    "Admin": ["General", "HR", "Legal", "Sales", "Technical", "Executive Compensation"],
    "Manager": ["General", "HR", "Legal", "Sales", "Technical"],
    "Employee": ["General", "Sales", "Technical"]
}
