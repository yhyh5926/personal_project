import joblib
import pandas as pd
import os


def predict_speed(link_id, target_time=None):
    # 1. 현재 파일(predictor.py)이 위치한 폴더의 절대 경로를 가져옵니다.
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. 같은 폴더(ml/) 내에 있는 traffic_model.pkl 파일의 절대 경로를 만듭니다.
    model_path = os.path.join(current_dir, 'traffic_model.pkl')

    # 모델 파일 존재 여부 확인
    if not os.path.exists(model_path):
        print(f"❌ 오류: 모델 파일을 찾을 수 없습니다.")
        print(f"탐색 경로: {model_path}")
        return None

    # 저장된 모델과 맵핑 정보 로드
    try:
        data = joblib.load(model_path)
        model = data['model']
        mapping = data['mapping']
    except Exception as e:
        print(f"❌ 모델 로딩 오류: {e}")
        return None

    # 시간 설정 (없으면 현재 시간)
    if target_time is None:
        target_time = pd.Timestamp.now()

    day = target_time.dayofweek
    hour = target_time.hour

    # link_id를 숫자로 변환
    encoded_id = mapping.get(link_id)

    if encoded_id is None:
        # 학습 데이터에 없는 도로인 경우
        return None

    # 예측 수행 (Feature 이름을 맞춰서 DataFrame으로 전달하는 것이 권장됨)
    input_data = pd.DataFrame([[day, hour, encoded_id]],
                              columns=['day_of_week', 'hour', 'link_id_encoded'])

    pred = model.predict(input_data)
    return pred[0]


# --- 테스트 실행 부분 ---
if __name__ == "__main__":
    test_link_id = "1220003800"
    result = predict_speed(test_link_id)

    if result is not None:
        print("-" * 30)
        print(f"📍 도로 ID: {test_link_id}")
        print(f"⏰ 예측 시간: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"🚀 AI 예상 속도: {result:.2f} km/h")
        print("-" * 30)
    else:
        print("❌ 예측에 실패했습니다. 도로 ID를 확인하거나 모델 파일을 확인하세요.")