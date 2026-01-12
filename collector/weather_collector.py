import requests
import datetime
from config import WEATHER_API_KEY, WEATHER_BASE_URL, AIRKOREA_API_KEY, AIRKOREA_BASE_URL, REQUEST_TIMEOUT
from db import insert_data

# -------------------------
# 기상청 실황
# -------------------------
def get_base_datetime_real_time():
    now = datetime.datetime.now()
    # API는 10분 단위로 제공되므로 가장 가까운 10분 단위로 내림
    minute = (now.minute // 10) * 10
    base_time = now.replace(minute=minute, second=0, microsecond=0).strftime("%H%M")
    return now.strftime("%Y%m%d"), base_time

def fetch_weather(nx: int, ny: int):
    base_date, base_time = get_base_datetime_real_time()
    params = {
        'serviceKey': WEATHER_API_KEY,
        'pageNo': 1,
        'numOfRows': 1000,
        'dataType': 'json',
        'base_date': base_date,
        'base_time': base_time,
        'nx': nx,
        'ny': ny,
    }

    response = requests.get(WEATHER_BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])

    if not items:
        print('기상청 API 응답 오류:', data)
        return None

    weather_data = {cat: None for cat in ["T1H","RN1","PTY","WSD","REH","VEC"]}
    for item in items:
        if item['category'] in weather_data:
            weather_data[item['category']] = float(item.get('obsrValue'))

    return weather_data

def get_wind_direction(vec: float) -> str:
    directions = ["북풍","북동풍","동풍","남동풍","남풍","남서풍","서풍","북서풍"]
    return directions[int((vec + 22.5) % 360 / 45)] if vec is not None else None

def format_weather_for_ui(weather):
    pty_dict = {"0":"비 없음","1":"비","2":"비/눈","3":"눈","4":"소나기"}
    return {
        "temperature": weather.get("T1H"),
        "precipitation": weather.get("RN1"),
        "rain_type": pty_dict.get(int(weather["PTY"]), '비 없음') if weather.get("PTY") is not None else "없음",
        "wind_speed": weather.get("WSD"),
        "humidity": weather.get("REH"),
        "wind_direction": get_wind_direction(weather.get("VEC"))
    }

# -------------------------
# AirKorea 미세먼지 예보 통보
# -------------------------
def fetch_airkorea_pm_forecast(region='서울'):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    params = {
        'serviceKey': AIRKOREA_API_KEY,
        'returnType': 'json',
        'numOfRows': 100,
        'pageNo': 1,
        'searchDate': today,
        'informCode': 'PM10'  # PM10/PM25/O3 등 예보 통보
    }

    resp = requests.get(AIRKOREA_BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    items = data.get('response', {}).get('body', {}).get('items', [])

    if not items:
        return {"region_grade": None, "overall": None, "description": None}

    # 오늘 기준 첫 번째 예보
    forecast_today = next((item for item in items if item['informData'] == today), items[0])

    # 서울 기준 등급
    grade_list = forecast_today.get('informGrade', "").split(',')
    region_grade = next((g.split(':')[1].strip() for g in grade_list if g.startswith(region)), None)

    return {
        'region_grade': region_grade,
        'overall': forecast_today.get('informOverall'),
        'description': forecast_today.get('informCause'),
        'announcement_time': forecast_today.get('dataTime')
    }

# -------------------------
# DB 저장
# -------------------------
def save_weather(region_code, weather, forecast):
    sql = """
        INSERT INTO WEATHER (weather_id,
                             region_code,
                             base_date,
                             base_time,
                             temperature,
                             precipitation,
                             rain_type,
                             wind_speed,
                             humidity,
                             wind_direction,
                             air_quality_grade,
                             air_overall,
                             air_description,
                             air_announcement_time,
                             collected_at)
        VALUES (WEATHER_SEQ.NEXTVAL,
                :1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,SYSDATE)
    """
    now = datetime.datetime.now()

    print('-----------',weather)
    params = (
        region_code,
        now.strftime("%Y%m%d"),
        now.strftime("%H%M"),
        weather.get("temperature"),
        weather.get("precipitation"),
        weather.get("rain_type"),
        weather.get("wind_speed"),
        weather.get("humidity"),
        weather.get("wind_direction"),
        forecast.get('region_grade'),
        forecast.get('overall'),
        forecast.get('description'),
        forecast.get('announcement_time')
    )
    insert_data(sql, params)

# -------------------------
# 실행
# -------------------------
if __name__ == '__main__':
    region_code = '서울'
    weather = fetch_weather(nx=60, ny=127)
    weather_ui = format_weather_for_ui(weather)
    forecast = fetch_airkorea_pm_forecast(region='서울')

    print(f"🌤 WEATHER_OBSR | 지역={region_code}")
    for k,v in weather_ui.items():
        print(f"{k}: {v}")
    print("💨 AirKorea 미세먼지 예보")
    print(f"서울 등급: {forecast['region_grade']}")
    print(f"전체 등급: {forecast['overall']}")
    print(f"설명: {forecast['description']}")

    save_weather(region_code, weather_ui, forecast)
