from flask import jsonify, request
from datetime import datetime, timedelta

from collector.weather_collector import (
    fetch_weather,
    fetch_airkorea_pm_forecast,
    format_weather_for_ui,
    save_weather
)
from utils.utils import latlng_to_grid

# ===============================
# 에어코리아 캐시 (메모리)
# ===============================
_air_cache = {
    "data": None,
    "expire": datetime.min
}


def get_cached_air_forecast(region='서울'):
    now = datetime.now()

    if _air_cache["data"] and now < _air_cache["expire"]:
        return _air_cache["data"]

    try:
        data = fetch_airkorea_pm_forecast(region=region)
        _air_cache["data"] = data
        _air_cache["expire"] = now + timedelta(minutes=30)
        return data
    except Exception as e:
        # 실패 시 기존 캐시라도 반환
        return _air_cache["data"]


# ===============================
# Routes
# ===============================
def routes(app):
    @app.route('/weather/current')
    def get_current_weather():
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)

        if lat is None or lng is None:
            return jsonify({"error": "좌표가 필요합니다"}), 400

        nx, ny = latlng_to_grid(lat, lng)

        weather_data = fetch_weather(nx, ny)
        if not weather_data:
            return jsonify({"error": "Weather data not available"}), 404

        weather_ui = format_weather_for_ui(weather_data)

        # 🔥 여기만 변경됨 (직접 호출 ❌ → 캐시 ⭕)
        forecast = get_cached_air_forecast(region='서울') or {}

        # 저장은 선택 (너 구조상 OK)
        save_weather('서울', weather_ui, forecast)

        return jsonify({
            "weather": weather_ui,
            "forecast": forecast
        })
