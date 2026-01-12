import cx_Oracle
from config import (
    ORACLE_HOST, ORACLE_PORT, ORACLE_SID, ORACLE_USER, ORACLE_PASSWORD
)


def get_connection():
    # Oracle DB 연결 생성
    dsn = cx_Oracle.makedsn(
        ORACLE_HOST,
        ORACLE_PORT,
        service_name=ORACLE_SID)

    conn = cx_Oracle.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=dsn,
    )
    return conn


def insert_data(sql: str, params: tuple):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
    except cx_Oracle.DatabaseError as e:
        print('DB insert error:', e)
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
