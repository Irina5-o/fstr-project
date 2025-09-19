import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        dbname=os.getenv('FSTR_DB_NAME'),
        user=os.getenv('FSTR_DB_LOGIN'),
        password=os.getenv('FSTR_DB_PASS'),
        host=os.getenv('FSTR_DB_HOST'),
        port=os.getenv('FSTR_DB_PORT')
    )
    print("✅ PostgreSQL подключена успешно!")
    conn.close()
except Exception as e:
    print(f"❌ Ошибка: {e}")

