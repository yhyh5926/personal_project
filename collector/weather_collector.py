import requests
import datetime
from config import WEATHER_API_KEY, WEATHER_BASE_URL, REQUEST_TIMEOUT, SEOUL_AIR_BASE_URL, SEOUL_AIR_API_KEY
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

    weather_data = {cat: None for cat in ["T1H", "RN1", "PTY", "WSD", "REH", "VEC"]}
    for item in items:
        if item['category'] in weather_data:
            weather_data[item['category']] = float(item.get('obsrValue'))

    return weather_data


def get_wind_direction(vec: float) -> str:
    directions = ["북풍", "북동풍", "동풍", "남동풍", "남풍", "남서풍", "서풍", "북서풍"]
    return directions[int((vec + 22.5) % 360 / 45)] if vec is not None else None


def format_weather_for_ui(weather):
    pty_dict = {
        0: "비 없음",
        1: "비",
        2: "비/눈",
        3: "눈",
        4: "소나기",
        5: "빗방울",
        6: "빗방울/눈날림",
        7: "눈날림"
    }

    pty_value = weather.get("PTY")

    try:
        pty_value = int(float(pty_value))
    except (TypeError, ValueError):
        pty_value = None

    return {
        "temperature": weather.get("T1H"),
        "precipitation": weather.get("RN1"),
        "rain_type": pty_dict.get(pty_value, "알 수 없음"),
        "wind_speed": weather.get("WSD"),
        "humidity": weather.get("REH"),
        "wind_direction": get_wind_direction(weather.get("VEC"))
    }


# -------------------------
# 미세먼지 데이터
# -------------------------

def fetch_air_quality_by_district(district_name):
    service = "ListAirQualityByDistrictService"
    url = f"{SEOUL_AIR_BASE_URL}/{SEOUL_AIR_API_KEY}/json/{service}/1/25"

    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    data = response.json()
    row_list = data.get(service, {}).get("row", [])

    for row in row_list:
        if row.get("MSRSTN_NM") == district_name:
            # Return only user-friendly essential information
            return {
                "district": row.get("MSRSTN_NM"),
                "measured_at": row.get("MSRMT_YMD"),
                "air_grade": row.get("CAI_GRD"),
                "pm10": row.get("PM"),
                "pm2_5": row.get("FPM"),
                "main_pollutant": row.get("CRST_SBSTN")
            }

    return None


# -------------------------
# DB 저장
# -------------------------
def save_weather(region, weather):
    sql = """
          INSERT INTO WEATHER (weather_id,
                               region,
                               temperature,
                               precipitation,
                               rain_type,
                               wind_speed,
                               humidity,
                               wind_direction,
                               air_grade,
                               pm10,
                               pm25,
                               main_pollutant,
                               measured_at,
                               collected_at)
          VALUES (WEATHER_SEQ.NEXTVAL,
                  :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11,
                  :12, SYSDATE) \
          """

    w = weather.get("weather")
    a = weather.get("air")

    params = (
        region,
        w.get("temperature"),
        w.get("precipitation"),
        w.get("rain_type"),
        w.get("wind_speed"),
        w.get("humidity"),
        w.get("wind_direction"),
        a.get('air_grade'),
        a.get('pm10'),
        a.get('pm2_5'),
        a.get('main_pollutant'),
        a.get("measured_at")
    )

    insert_data(sql, params)

