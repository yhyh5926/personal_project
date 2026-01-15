from flask import jsonify, request

from collector.traffic_collector import fetch_traffic
from ml.predictor import predict_speed


def routes(app):
    @app.route("/api/traffic", methods=['POST'])
    def traffic_api():
        road = request.get_json()
        data = fetch_traffic(road)

        if not data:
            return jsonify({"error": f"{road['link_id']}에 대한 교통 데이터 없음"}), 200
        print('요청 성공\n', data)
        return jsonify({
            "link_id": data["LINK_ID"],
            "avg_speed": data["AVG_SPEED"],
            "congestion_level": data["CONGESTION_LEVEL"],
            'name': road['name'],
            'prcs_trv_time': data['PRCS_TRV_TIME'],
        })

    # AI 예측 API
    @app.route('/api/predict/<link_id>')
    def api_predict_traffic(link_id):
        print(f"🚀 AI 요청 수신됨! link_id: {link_id}")
        try:
            # ml/predictor.py의 함수 호출
            prediction = predict_speed(link_id)

            if prediction is None:
                return jsonify({"error": "학습 데이터가 없는 도로입니다."}), 404

            return jsonify({
                "link_id": link_id,
                "predicted_speed": round(float(prediction), 1)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
