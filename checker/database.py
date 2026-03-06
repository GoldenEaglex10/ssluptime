import sqlite3, os
from datetime import datetime

DB_PATH = os.path.join("db", "alerts.db")

def init_db():
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Alerts log
    cur.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT,
            timestamp TEXT,
            alert_type TEXT,
            details TEXT
        )
    ''')

    # Active issues table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS active_issues (
            domain TEXT PRIMARY KEY,
            alert_type TEXT,
            details TEXT,
            first_seen TEXT
        )
    ''')

    conn.commit()
    conn.close()


def log_alert(domain, alert_type, details):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        '''INSERT INTO alerts (domain, timestamp, alert_type, details)
           VALUES (?, ?, ?, ?)''',
        (domain, datetime.now().isoformat(), alert_type, details)
    )
    conn.commit()
    conn.close()


def is_issue_active(domain, alert_type, details, cooldown_hours=6):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        '''SELECT first_seen FROM active_issues 
           WHERE domain=? AND alert_type=? AND details=?''',
        (domain, alert_type, details)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return False

    first_seen = datetime.fromisoformat(row[0])
    age_hours = (datetime.now() - first_seen).total_seconds() / 3600

    return age_hours < cooldown_hours

def set_issue_active(domain, alert_type, details):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        '''INSERT OR REPLACE INTO active_issues 
           (domain, alert_type, details, first_seen) 
           VALUES (?, ?, ?, ?)''',
        (domain, alert_type, details, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def clear_active_issue(domain):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('DELETE FROM active_issues WHERE domain=?', (domain,))
    conn.commit()
    conn.close()
