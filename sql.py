import sqlite3

# 데이터베이스 이름
db_name = 'fpwd.db'

# 데이터베이스 연결 및 테이블 생성
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# 테이블 생성 (예: 사용자 정보 테이블)
cursor.execute('''
CREATE TABLE IF NOT EXISTS fpwd (
    fname TEXT PRIMARY KEY,
    gesture_1 TEXT,
    gesture_2 TEXT,
    gesture_3 TEXT,
    gesture_4 TEXT
)
''')

# 데이터 삽입
cursor.execute('INSERT INTO fpwd (fname, gesture_1, gesture_2, gesture_3, gesture_4) VALUES (?, ?, ?, ?, ?)', ('기밀문서.docx', 'One_1', 'Three_3', 'Nine_9', 'Seven_7'))

# 커밋과 연결 종료
conn.commit()

# 데이터 조회
cursor.execute('SELECT * FROM fpwd')
rows = cursor.fetchall()

for row in rows:
    print(row)

# 연결 닫기
conn.close()
