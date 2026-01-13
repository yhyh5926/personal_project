from flask import jsonify, request

from collector.weather_collector import (
    fetch_weather,
    format_weather_for_ui,
    fetch_air_quality_by_district,
    save_weather
)
from utils.utils import latlng_to_grid


def routes(app):
    @app.route('/api/weather')
    def get_current_weather():
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        district = request.args.get('district')

        if lat is None or lng is None:
            return jsonify({"error": "좌표가 필요합니다"}), 400

        # 격자 구하기
        nx, ny = latlng_to_grid(lat, lng)

        weather_data = fetch_weather(nx, ny)
        air_data = fetch_air_quality_by_district(district)

        if not weather_data:
            return jsonify({"error": "Weather data not available"}), 404

        if not air_data:
            return jsonify({'error': 'air data not available'}), 404

        formatted_weather = format_weather_for_ui(weather_data)

        # 공기 데이터 간단히 정리
        air_info = {
            "air_grade": air_data.get("air_grade", "정보 없음"),
            "pm10": air_data.get("pm10", "-"),
            "pm2_5": air_data.get("pm2_5", "-"),
            "main_pollutant": air_data.get("main_pollutant", "-"),
            "measured_at": air_data.get("measured_at", "-")
        }

        # 날씨 + 공기 데이터 통합 리턴
        response = {
            "weather": formatted_weather,
            "air": air_info
        }
        save_weather(district, response)
        return jsonify(response)
