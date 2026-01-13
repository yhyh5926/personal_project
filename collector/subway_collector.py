import requests
from config import SUBWAY_API_KEY, SUBWAY_BASE_URL, REQUEST_TIMEOUT
from utils.utils import SUBWAY_LINE_MAP, seconds_to_min_sec


def fetch_subway_arrival(station_name: str):
    """
    서울시 지하철 실시간 도착 정보를 가져오는 콜렉터
    """
    url = f"{SUBWAY_BASE_URL}/{SUBWAY_API_KEY}/json/realtimeStationArrival/1/10/{station_name}/"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"[ERROR] API 요청 실패: {e}")
        return []
    except ValueError as e:
        print(f"[ERROR] JSON 파싱 실패: {e}")
        return []

    if "errorMessage" in data and data["errorMessage"].get("code") != "INFO-000":
        print(f"[ERROR] API 응답 코드: {data['errorMessage'].get('code')}, 메시지: {data['errorMessage'].get('message')}")
        return []

    rows = data.get("realtimeArrivalList", [])
    results = []

    for row in rows:
        subway_id = str(row.get("subwayId", ""))
        barvlDt_sec = int(row.get("barvlDt", 0)) if row.get("barvlDt") else 0
        results.append({
            "line": SUBWAY_LINE_MAP.get(subway_id, subway_id),
            "train_type": row.get("btrainSttus", ""),
            "direction": row.get("updnLine", ""),
            "destination": row.get("trainLineNm", ""),
            "current_station": row.get("statnNm", ""),
            "arrival_in": seconds_to_min_sec(barvlDt_sec),
            "arrival_message": row.get("arvlMsg2", "")
        }
        )
    return results


# 테스트용
if __name__ == "__main__":
    trains = fetch_subway_arrival("강남")
    for t in trains:
        print(f"{t['호선']} | {t['열차종류']} | {t['상하행']} | {t['도착방면']} | 도착까지: {t['도착까지']}")
