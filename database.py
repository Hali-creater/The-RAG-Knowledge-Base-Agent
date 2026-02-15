import sqlite3
import datetime

DB_NAME = "leads.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            source_platform TEXT,
            intent_type TEXT,
            property_details TEXT,
            price REAL,
            location TEXT,
            lead_score INTEGER,
            status TEXT DEFAULT 'New',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            post_title TEXT,
            full_description TEXT,
            intent_confidence REAL,
            UNIQUE(source_platform, phone, email, full_description)
        )
    """)
    conn.commit()
    conn.close()

def save_lead(lead_data):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO leads (
                name, phone, email, source_platform, intent_type,
                property_details, price, location, lead_score,
                status, post_title, full_description, intent_confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead_data.get('name'),
            lead_data.get('phone'),
            lead_data.get('email'),
            lead_data.get('source_platform'),
            lead_data.get('intent_type'),
            lead_data.get('property_details'),
            lead_data.get('price'),
            lead_data.get('location'),
            lead_data.get('lead_score'),
            lead_data.get('status', 'New'),
            lead_data.get('post_title'),
            lead_data.get('full_description'),
            lead_data.get('intent_confidence')
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def get_all_leads(filters=None):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM leads"
    params = []

    if filters:
        allowed_columns = ["intent_type", "status", "location"]
        conditions = []
        for key, value in filters.items():
            if key in allowed_columns and value:
                conditions.append(f"{key} = ?")
                params.append(value)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY timestamp DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    leads = [dict(row) for row in rows]
    conn.close()
    return leads

def update_lead_status(lead_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leads SET status = ? WHERE id = ?", (status, lead_id))
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
            SUM(CASE WHEN intent_type = 'Seller' THEN 1 ELSE 0 END) as sellers,
            SUM(CASE WHEN intent_type = 'Buyer' THEN 1 ELSE 0 END) as buyers,
            AVG(lead_score) as avg_score
        FROM leads
        WHERE date(timestamp) = ?
    """, (today,))
    summary = cursor.fetchone()
    conn.close()
    return {
        "total": summary[0] or 0,
        "sellers": summary[1] or 0,
        "buyers": summary[2] or 0,
        "avg_score": summary[3] or 0
    }

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
