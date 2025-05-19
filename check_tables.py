import sqlite3

conn = sqlite3.connect('spending.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("✅ 현재 존재하는 테이블 목록:")
for table in tables:
    print(" -", table[0])

conn.close()
