import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl
from datetime import timedelta

from collector.db import select_data, select_district

# ==================================================
# 한글 폰트 설정 (Windows - PyCharm 기준)
# ==================================================
font_path = "C:/02WorkSpaces/personal_project/resData/malgun.ttf"  # 맑은 고딕
font_name = fm.FontProperties(fname=font_path).get_name()

mpl.rcParams["font.family"] = font_name
mpl.rcParams["axes.unicode_minus"] = False  # - 기호 깨짐 방지


# ==================================================
# 최근 48시간 WEATHER 데이터 로드
# ==================================================
def load_weather_df():
    sql = """
          SELECT region,
                 temperature,
                 pm10,
                 air_grade,
                 measured_at

          FROM WEATHER
          WHERE measured_at >= TO_CHAR(
                  SYSDATE - INTERVAL '48' HOUR,
                  'YYYYMMDDHH24MI'
                               )
          ORDER BY measured_at \
          """

    rows = select_data(sql)

    df = pd.DataFrame(
        rows,
        columns=["region", "temperature", "pm10", "air_grade", "measured_at"]
    )

    return df


# ==================================================
# 기온 + 미세먼지 그래프 생성 (단일 PNG)
# ==================================================


def generate_weather_bar_plot(df):
    if df.empty:
        raise ValueError("그래프를 생성할 데이터가 없습니다.")

    # measured_at → datetime
    df["measured_at"] = pd.to_datetime(df["measured_at"].astype(str), format="%Y%m%d%H%M")
    df["pm10"] = pd.to_numeric(df["pm10"], errors="coerce")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")

    # 최근 24시간
    end_time = df["measured_at"].max()
    start_time = end_time - timedelta(hours=24)
    df = df[df["measured_at"] >= start_time]

    # air_grade 컬럼이 없는 경우 생성
    if "air_grade" not in df.columns:
        df["air_grade"] = None

    # 결측값은 "알 수 없음"으로 채우기
    df["air_grade"] = df["air_grade"].fillna("알 수 없음")

    # 각 구별 최근 데이터 평균
    summary = df.groupby("region").agg(
        avg_temp=("temperature", "mean"),
        avg_pm10=("pm10", "mean"),
        air_grade=("air_grade", lambda x: x.mode()[0] if not x.mode().empty else "알 수 없음")
    ).reset_index()

    regions = summary["region"]
    temps = summary["avg_temp"]
    pm10s = summary["avg_pm10"]
    air_grades = summary["air_grade"]

    x = range(len(regions))
    width = 0.35

    plt.figure(figsize=(12, 6))

    # 기온 막대
    plt.bar(x, temps, width=width, color="salmon", label="기온 (℃)")
    # 미세먼지 막대
    plt.bar([i + width for i in x], pm10s, width=width, color="skyblue", label="미세먼지 PM10 (㎍/㎥)")

    # X축 레이블
    plt.xticks([i + width / 2 for i in x], regions, rotation=45, ha="right")
    plt.ylabel("값")
    plt.title("최근 24시간 구별 기온 · 미세먼지 비교")

    # 막대 위 텍스트 표시
    for i, (t, pm, grade) in enumerate(zip(temps, pm10s, air_grades)):
        plt.text(i, t + 0.5, f"{t:.1f}℃", ha="center", va="bottom", fontsize=9, color="red")
        plt.text(i + width, pm + 0.5, f"{pm:.0f} ({grade})", ha="center", va="bottom", fontsize=9, color="blue")

    plt.legend()
    plt.tight_layout()

    # PNG 저장
    output_path = "C:/02WorkSpaces/personal_project/backend/static/images/weather_bar.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()

    web_path = "/static/images/weather_bar.png"
    return web_path


def generate_district_bar_plot(district_name):
    """
    해당 구의 최신 데이터 기준 최대 24개
    시간대별 기온·미세먼지 막대 그래프
    (특정 시간만 미세먼지 점검중 처리)
    """
    rows = select_district(district_name)
    if not rows:
        raise ValueError(f"{district_name}의 데이터가 없습니다.")

    df = pd.DataFrame(
        rows,
        columns=["region", "temperature", "pm10", "air_grade", "measured_at"]
    )

    # 시간 변환
    df["measured_at"] = pd.to_datetime(
        df["measured_at"].astype(str),
        format="%Y%m%d%H%M"
    )

    # 기온
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")

    # 미세먼지 → 숫자 변환 실패한 시간만 NaN
    df["pm10_raw"] = df["pm10"]  # 원본 보관
    df["pm10"] = pd.to_numeric(df["pm10"], errors="coerce")

    # 점검중 시간대 판별
    df["pm10_status"] = df["pm10"].isna()

    # 점검중 시간 → 0
    df.loc[df["pm10_status"], "pm10"] = 0

    # air_grade 처리
    df["air_grade"] = df["air_grade"].fillna("점검중")

    x = list(range(len(df)))
    width = 0.4

    plt.figure(figsize=(14, 6))

    # 기온
    plt.bar(
        [i - width / 2 for i in x],
        df["temperature"],
        width=width,
        color="salmon",
        label="기온(℃)"
    )

    # 미세먼지
    plt.bar(
        [i + width / 2 for i in x],
        df["pm10"],
        width=width,
        color="skyblue",
        alpha=0.75,
        label="PM10(㎍/㎥)"
    )

    # X축
    step = max(1, len(df) // 8)
    plt.xticks(
        x[::step],
        df["measured_at"].dt.strftime("%m-%d %H:%M")[::step],
        rotation=45,
        ha="right"
    )

    plt.xlabel("시간")
    plt.ylabel("값")
    plt.title(f"{district_name} 시간별 기온 · 미세먼지")
    plt.legend()

    # 텍스트 표시
    for i, row in df.iterrows():

        # 기온
        if pd.notna(row["temperature"]):
            plt.text(
                i - width / 2,
                row["temperature"] + 0.3,
                f"{row['temperature']:.1f}℃",
                fontsize=8,
                color="red",
                ha="center"
            )

        # 미세먼지
        if row["pm10_status"]:
            plt.text(
                i + width / 2,
                0.5,
                "점검중",
                fontsize=8,
                color="gray",
                rotation=90,
                ha="center"
            )
        else:
            plt.text(
                i + width / 2,
                row["pm10"] + 1,
                row["air_grade"],
                fontsize=8,
                color="#555555",
                rotation=45,
                ha="center"
            )

    plt.tight_layout()

    # 저장
    output_dir = "C:/02WorkSpaces/personal_project/backend/static/images"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{district_name}_bar.png")
    plt.savefig(output_path)
    plt.close()

    return f"/static/images/{district_name}_bar.png"


# ==================================================
# 단독 실행용 (테스트)
# ==================================================
if __name__ == "__main__":
    df = load_weather_df()
    path = generate_weather_bar_plot(df)
    print("그래프 생성 완료:", path)

    district_path = generate_district_bar_plot('강남구')
    print('48시간 그래프 생성 완료:', district_path)
