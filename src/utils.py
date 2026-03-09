import os
import hashlib

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    dirs = ['data/documents', 'data/chroma_db', 'uploads']
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
