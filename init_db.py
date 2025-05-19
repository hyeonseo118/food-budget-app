import sqlite3

conn = sqlite3.connect('spending.db')
c = conn.cursor()

# 지출 내역 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    place TEXT,
    amount INTEGER,
    category TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 예산 설정 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS budget_settings (
    id INTEGER PRIMARY KEY,
    amount INTEGER
)
''')

# 기본 예산이 없으면 0원으로 설정
c.execute("SELECT COUNT(*) FROM budget_settings")
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO budget_settings (id, amount) VALUES (1, 0)")

conn.commit()
conn.close()

print("✅ spending.db 초기화 완료 (expenses + budget_settings 테이블)")
