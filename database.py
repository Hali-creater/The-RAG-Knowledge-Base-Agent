import sqlite3
import datetime
import os
import hashlib
import csv
from io import StringIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "leads.db")

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            description TEXT,
            url TEXT UNIQUE,
            location TEXT,
            lead_type TEXT,
            phone TEXT,
            email TEXT,
            intent_score INTEGER,
            intent_level TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'New',
            notes TEXT,
            content_hash TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_content_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest() if text else ""

def save_lead(lead_data):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if URL exists
    url = lead_data.get('url')
    if not url:
        return

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO leads (
                source, title, description, url, location,
                lead_type, phone, email, intent_score,
                intent_level, status, notes, content_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead_data.get('source'),
            lead_data.get('title'),
            lead_data.get('description'),
            url,
            lead_data.get('location'),
            lead_data.get('lead_type'),
            lead_data.get('phone'),
            lead_data.get('email'),
            lead_data.get('intent_score'),
            lead_data.get('intent_level'),
            lead_data.get('status', 'New'),
            lead_data.get('notes', ''),
            lead_data.get('content_hash')
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def get_all_leads(filters=None, sort_by="created_at", sort_order="DESC"):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM leads"
    params = []

    if filters:
        allowed_columns = ["source", "lead_type", "status", "intent_level", "location"]
        conditions = []
        for key, value in filters.items():
            if key in allowed_columns and value:
                conditions.append(f"{key} = ?")
                params.append(value)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

    # Basic sorting validation
    allowed_sort = ["intent_score", "created_at"]
    if sort_by not in allowed_sort:
        sort_by = "created_at"
    if sort_order not in ["ASC", "DESC"]:
        sort_order = "DESC"

    query += f" ORDER BY {sort_by} {sort_order}"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    leads = [dict(row) for row in rows]
    conn.close()
    return leads

def update_lead(lead_id, updates):
    conn = get_connection()
    cursor = conn.cursor()
    for key, value in updates.items():
        if key in ["status", "notes"]:
            cursor.execute(f"UPDATE leads SET {key} = ? WHERE id = ?", (value, lead_id))
    conn.commit()
    conn.close()

def delete_lead(lead_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    conn.commit()
    conn.close()

def get_daily_summary():
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.date.today().isoformat()
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN lead_type = 'Seller' THEN 1 ELSE 0 END) as sellers,
            SUM(CASE WHEN lead_type = 'Buyer' THEN 1 ELSE 0 END) as buyers,
            AVG(intent_score) as avg_score
        FROM leads
        WHERE date(created_at) = ?
    """, (today,))
    summary = cursor.fetchone()
    conn.close()
    return {
        "total": summary[0] or 0,
        "sellers": summary[1] or 0,
        "buyers": summary[2] or 0,
        "avg_score": summary[3] or 0
    }

def export_to_csv(leads):
    output = StringIO()
    # Using 'Date' instead of 'created_at' in the CSV header
    writer = csv.DictWriter(output, fieldnames=[
        "title", "source", "location", "lead_type", "phone", "email",
        "intent_score", "intent_level", "url", "Date", "status", "notes"
    ], extrasaction='ignore')
    writer.writeheader()
    for lead in leads:
        # Map created_at to Date for header consistency
        lead_copy = dict(lead)
        lead_copy["Date"] = lead_copy.get("created_at")
        writer.writerow(lead_copy)
    return output.getvalue()

if __name__ == "__main__":
    init_db()
    print("Database updated.")
