from flask import jsonify, request

from collector.traffic_collector import fetch_traffic


def routes(app):
    @app.route("/traffic", methods=['POST'])
    def traffic_api():
        road = request.get_json()
        data = fetch_traffic(road)

        if not data:
            return jsonify({"error": f"{road['link_id']}에 대한 교통 데이터 없음"}), 200

        return jsonify({
            "link_id": data["LINK_ID"],
            "avg_speed": data["AVG_SPEED"],
            "congestion_level": data["CONGESTION_LEVEL"],
            'name': road['name'],
            'prcs_trv_time': data['PRCS_TRV_TIME'],
        })
