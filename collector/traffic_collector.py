import requests
import xmltodict
from config import TRAFFIC_API_KEY, TRAFFIC_BASE_URL, REQUEST_TIMEOUT
from db import insert_data

def fetch_traffic(road):

    url = f"{TRAFFIC_BASE_URL}/{TRAFFIC_API_KEY}/xml/TrafficInfo/1/1/{road['link_id']}"

    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    data = xmltodict.parse(response.text)
    traffic_info = data.get("TrafficInfo", {}).get("row")

    if not traffic_info:
        print("⚠️ 교통 데이터 없음")
        return None

    if isinstance(traffic_info, dict):
        traffic_info = [traffic_info]

    row = traffic_info[0]
    traffic_data = {
        "LINK_ID": row.get("link_id"),
        "PRCS_SPD": row.get("prcs_spd"),
        "PRCS_TRV_TIME": row.get("prcs_trv_time"),
        "AVG_SPEED": float(row.get("prcs_spd") or 0),
        "CONGESTION_LEVEL": calculate_congestion(row.get("prcs_spd") or 0),
        'ROAD_NAME': road.get("name"),
    }


    save_traffic(traffic_data)
    return traffic_data

def calculate_congestion(speed):
    try:
        speed = float(speed)
    except (TypeError, ValueError):
        return 4  # 데이터 없으면 최악(정체) 처리

    if speed >= 40:
        return 1
    elif speed >= 20:
        return 2
    elif speed >= 10:
        return 3
    else:
        return 4

def save_traffic(row):
    avg_speed = float(row["PRCS_SPD"] or 0)
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
            :1, :2, NULL, NULL, :3, :4, SYSDATE
        )
    """

    params = (
        row["LINK_ID"],
        row['ROAD_NAME'],
        avg_speed,
        congestion_level
    )

    insert_data(sql, params)


