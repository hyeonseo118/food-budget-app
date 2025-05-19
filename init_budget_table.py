# init_budget_table.py
import sqlite3

conn = sqlite3.connect('budget.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS budget_settings (
    id INTEGER PRIMARY KEY,
    amount INTEGER NOT NULL
)
''')

# 초기 예산값을 0으로 설정 (1명 사용자 기준)
cursor.execute("SELECT COUNT(*) FROM budget_settings")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO budget_settings (id, amount) VALUES (1, 0)")

conn.commit()
conn.close()
print("✅ 예산 테이블 생성 완료")
