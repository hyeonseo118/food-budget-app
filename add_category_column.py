# add_category_column.py
import sqlite3

conn = sqlite3.connect('budget.db')
cursor = conn.cursor()

# category 컬럼이 없으면 추가
cursor.execute("PRAGMA table_info(expenses)")
columns = [col[1] for col in cursor.fetchall()]
if 'category' not in columns:
    cursor.execute("ALTER TABLE expenses ADD COLUMN category TEXT DEFAULT '기타'")
    print("✅ category 컬럼 추가 완료")
else:
    print("⚠️ 이미 category 컬럼이 있음")

conn.commit()
conn.close()
