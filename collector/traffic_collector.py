import requests
import xmltodict
from config import TRAFFIC_API_KEY, TRAFFIC_BASE_URL, REQUEST_TIMEOUT
from db import insert_data


def fetch_traffic(link_id):
    url = f"{TRAFFIC_BASE_URL}/{TRAFFIC_API_KEY}/xml/TrafficInfo/1/5/{link_id}"

    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    data = xmltodict.parse(response.text)

    traffic_info = data.get("TrafficInfo", {}).get("row")

    if not traffic_info:
        print("⚠️ 교통 데이터 없음")
        return

    if isinstance(traffic_info, dict):
        traffic_info = [traffic_info]

    for row in traffic_info:
        traffic_data = {
            "LINK_ID": row.get("link_id"),
            "PRCS_SPD": row.get("prcs_spd"),
            "PRCS_TRV_TIME": row.get("prcs_trv_time"),
        }

        print(traffic_data)
        save_traffic(traffic_data)


def calculate_congestion(speed):
    speed = float(speed)

    if speed >= 40:
        return 1
    elif speed >= 20:
        return 2
    elif speed >= 10:
        return 3
    else:
        return 4


def save_traffic(row):
    avg_speed = float(row["PRCS_SPD"])
    congestion_level = calculate_congestion(avg_speed)

    sql = """
        INSERT INTO TRAFFIC (
            traffic_id,
            link_id,
            road_name,
            start_point,
            end_point,
            avg_speed,
            congestion_level,
            collected_at
        ) VALUES (
            TRAFFIC_SEQ.NEXTVAL,
            :1, NULL, NULL, NULL, :2, :3, SYSDATE
        )
    """

    params = (
        row["LINK_ID"],
        avg_speed,
        congestion_level
    )

    insert_data(sql, params)
    print(
        f"TRAFFIC 저장 완료 | LINK_ID={row['LINK_ID']} "
        f"| 속도={avg_speed}km/h | 혼잡도={congestion_level}"
    )



if __name__ == "__main__":
    fetch_traffic(link_id="1220003800")
