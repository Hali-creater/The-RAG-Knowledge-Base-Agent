import os
import sys
import subprocess
import sqlite3
from dotenv import load_dotenv

def check_python_version():
    print(f"[*] Python Version: {sys.version}")
    return True

def check_dependencies():
    required = ["fastapi", "uvicorn", "apscheduler", "requests", "bs4", "playwright", "spacy", "sklearn", "pandas", "praw"]
    missing = []
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            missing.append(lib)

    if missing:
        print(f"[!] Missing Libraries: {', '.join(missing)}")
        print("    Run: pip install -r requirements.txt")
        return False
    print("[+] All core libraries found.")
    return True

def check_spacy():
    import spacy
    try:
        spacy.load("en_core_web_sm")
        print("[+] Spacy model 'en_core_web_sm' is loaded.")
        return True
    except OSError:
        print("[!] Spacy model 'en_core_web_sm' not found.")
        print("    Run: python -m spacy download en_core_web_sm")
        return False

def check_env():
    load_dotenv()
    vars_to_check = {
        "REDDIT_CLIENT_ID": "Reddit API",
        "REDDIT_CLIENT_SECRET": "Reddit API",
        "IMAP_USER": "Gmail IMAP",
        "IMAP_PASSWORD": "Gmail IMAP",
        "SMTP_USER": "Email Notifications",
        "SMTP_PASSWORD": "Email Notifications"
    }

    missing = []
    for var, name in vars_to_check.items():
        if not os.getenv(var) or "your_" in os.getenv(var):
            missing.append(f"{var} ({name})")

    if missing:
        print("[!] Missing or Default Environment Variables:")
        for m in missing:
            print(f"    - {m}")
        print("    Update your .env file with real credentials.")
        return False
    print("[+] Environment variables seem to be configured.")
    return True

def check_db():
    try:
        conn = sqlite3.connect("leads.db")
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM leads")
        count = cursor.fetchone()[0]
        print(f"[+] Database 'leads.db' is accessible. Current Lead Count: {count}")
        conn.close()
        return True
    except Exception as e:
        print(f"[!] Database Error: {e}")
        return False

def run_diagnostics():
    print("=== REAL ESTATE AI SYSTEM DIAGNOSTIC ===\n")
    results = [
        check_python_version(),
        check_dependencies(),
        check_spacy(),
        check_env(),
        check_db()
    ]

    print("\n" + "="*40)
    if all(results):
        print("✅ SYSTEM READY: Your environment is correctly configured.")
    else:
        print("❌ ACTION REQUIRED: Fix the issues listed above to get results.")
    print("="*40)

if __name__ == "__main__":
    run_diagnostics()
