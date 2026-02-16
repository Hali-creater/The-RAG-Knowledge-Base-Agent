import os
import hashlib

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def ensure_dirs():
    dirs = ['data/documents', 'data/chroma_db', 'uploads']
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
