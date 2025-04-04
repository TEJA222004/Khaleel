import sqlite3

# Connect to SQLite Database (creates if not exists)
conn = sqlite3.connect("faces.db")
cursor = conn.cursor()

# Create a table to store student faces
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        class TEXT NOT NULL,
        section TEXT NOT NULL,
        year TEXT NOT NULL,
        encoding BLOB NOT NULL,
        image_path TEXT NOT NULL
    )
''')

# Commit changes and close connection
conn.commit()
conn.close()

print("✅ Database 'faces.db' and table 'students' created successfully with additional fields!")
