import sqlite3

# DB 연결
conn = sqlite3.connect('spending.db')
c = conn.cursor()

# 찜한 식당 테이블 생성
c.execute('''
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    lat REAL,
    lng REAL
)
''')

conn.commit()
conn.close()

print("✅ favorites 테이블 생성 완료")
