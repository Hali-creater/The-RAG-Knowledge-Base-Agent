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
    download_nltk_data()
