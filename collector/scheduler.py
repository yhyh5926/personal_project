import time
from weather_collector import fetch_weather
from traffic_collector import fetch_traffic

# 수집 주기 (초)
WEATHER_INTERVAL = 10 * 60
TRAFFIC_INTERVAL = 5 * 60
AIR_POLLUTION_INTERVAL = 10 * 60

def run_scheduler():
    last_weather_time = 0
    last_traffic_time = 0

    while True:
        now = time.time()

        # 날씨 수집
        if now - last_weather_time >= WEATHER_INTERVAL:
            print("🌦 날씨 데이터 수집 시작")
            try:
                fetch_weather(
                    nx=60,
                    ny=127,
                    region_code='SEOUL_JONGRO',
                )
                last_weather_time = now
            except Exception as e:
                print("날씨 수집 실패:", e)

        # 교통 수집
        if now - last_traffic_time >= TRAFFIC_INTERVAL:
            print("🚗 교통 데이터 수집 시작")
            try:
                fetch_traffic(link_id="1220003800")
                last_traffic_time = now
            except Exception as e:
                print("교통 수집 실패:", e)

        time.sleep(1)


if __name__ == "__main__":
    run_scheduler()
