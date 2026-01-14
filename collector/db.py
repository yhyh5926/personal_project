import cx_Oracle
from collector.config import (
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

#데이터 입력
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


def select_data(sql: str, params: tuple = None):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        rows = cursor.fetchall()
        return rows

    except cx_Oracle.DatabaseError as e:
        print('DB select error:', e)
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def select_district(district_name: str):
    """
    해당 구의 최신 데이터 기준으로 과거 최대 24개 조회
    (데이터가 1개여도 그대로 반환)
    """
    sql = """
        SELECT region,
               temperature,
               pm10,
               air_grade,
               measured_at
        FROM (
            SELECT region,
                   temperature,
                   pm10,
                   air_grade,
                   measured_at
            FROM WEATHER
            WHERE region = :1
            ORDER BY measured_at DESC
        )
        WHERE ROWNUM <= 24
        ORDER BY measured_at
    """
    return select_data(sql, (district_name,))
