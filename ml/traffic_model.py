import pandas as pd
import cx_Oracle
from sklearn.ensemble import RandomForestRegressor
import joblib
import os


def train_traffic_model():
    # 현재 파일(train_model.py)이 있는 폴더 위치를 파악
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 저장될 파일의 절대 경로 설정 (항상 ml 폴더 바로 아래 저장)
    model_save_path = os.path.join(current_dir, 'traffic_model.pkl')

    # 1. DB 연결 설정
    dsn = cx_Oracle.makedsn("localhost", 1521, "xe")
    conn = cx_Oracle.connect("project", "1234", dsn)

    try:
        # 2. 데이터 불러오기
        query = """
                SELECT LINK_ID, AVG_SPEED, COLLECTED_AT
                FROM TRAFFIC
                WHERE AVG_SPEED IS NOT NULL
                """
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=['link_id', 'avg_speed', 'collected_at'])

        if len(df) < 10:
            print(f"현재 데이터 수: {len(df)}개. 데이터가 부족합니다.")
            return

        # 3. 데이터 전처리
        df['collected_at'] = pd.to_datetime(df['collected_at'])
        df['day_of_week'] = df['collected_at'].dt.dayofweek
        df['hour'] = df['collected_at'].dt.hour
        df['link_id_encoded'] = df['link_id'].astype('category').cat.codes

        # 매핑 정보 생성
        reverse_mapping = dict(zip(df['link_id'], df['link_id_encoded']))

        # 4. 학습 데이터 분리
        X = df[['day_of_week', 'hour', 'link_id_encoded']]
        y = df['avg_speed']

        # 5. 모델 생성 및 학습
        print(f"총 {len(df)}개의 데이터로 모델 학습 중...")
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # 6. 결과 저장 (중첩 폴더 방지)
        joblib.dump({
            'model': model,
            'mapping': reverse_mapping
        }, model_save_path)

        print(f"✅ 학습 완료! 파일 위치: {model_save_path}")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    train_traffic_model()