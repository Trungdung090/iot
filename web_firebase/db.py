import sqlite3

conn = sqlite3.connect('my_db.db')
cursor = conn.cursor()
    
cursor.execute('''
CREATE TABLE IF NOT EXISTS sense_data(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hum  REAL NOT NULL,
    temp REAL NOT NULL
)
''')
conn.commit()
conn.close()