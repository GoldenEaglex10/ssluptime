import sqlite3
import pandas as pd

conn = sqlite3.connect("db/alerts.db")
df = pd.read_sql("SELECT * FROM alerts", conn)
df.to_csv("alert_history.csv", index=False)
print("[✓] Exported to alert_history.csv")
