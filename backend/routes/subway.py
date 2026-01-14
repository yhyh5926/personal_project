from flask import request, jsonify
from collector.subway_collector import fetch_subway_arrival

def routes(app):
    @app.route('/api/subway')
    def subway_api():
        station = request.args.get('station')

        if not station:
            return jsonify({"error": "station parameter is required"}), 400
        station_data = fetch_subway_arrival(station)
        print('요청 성공\n',station_data)
        return jsonify(station_data)
