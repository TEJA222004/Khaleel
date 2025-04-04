import sqlite3

conn = sqlite3.connect("faces.db")
cursor = conn.cursor()

name_to_delete = input("Enter the name to delete: ")

cursor.execute("DELETE FROM students WHERE name = ?", (name_to_delete,))
conn.commit()
conn.close()

print(f"✅ Deleted {name_to_delete} from the database. Now you can register again!")
