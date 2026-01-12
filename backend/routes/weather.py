from flask import Blueprint, jsonify
from collector.weather_collector import fetch_weather, fetch_airkorea_pm_forecast, format_weather_for_ui,save_weather

bp = Blueprint('weather', __name__)


# 현재 날씨 + 미세먼지 예보 API
@bp.route('/current/<region_code>')
def get_current_weather(region_code):
    # 예: 서울 종로 좌표
    nx, ny = 60, 127

    weather_data = fetch_weather(nx, ny)
    if not weather_data:
        return jsonify({"error": "Weather data not available"}), 404

    weather_ui = format_weather_for_ui(weather_data)

    print('-asdasdas----------',weather_ui)

    forecast = fetch_airkorea_pm_forecast(region=region_code)

    save_weather(region_code, weather_ui, forecast)

    result = {
        "weather": weather_ui,
        "forecast": forecast
    }
    return jsonify(result)
