# ===============================
# 공공 API KEY
# ===============================

# 기상청 API 키 (공공데이터포털)
WEATHER_API_KEY = "e7394abb53610b5a6e71de1ecffd610b33dfa9511f809b7eaea02ba4eb5b0b7e"

# 서울시 교통 API 키
TRAFFIC_API_KEY = "4577756d6d79683935356b6f496a58"

# 서울 에어 API 키
SEOUL_AIR_API_KEY = '4f7369786679683936374f625a6169'

# 지하철 API 키
SUBWAY_API_KEY = "6b7851695979683933315a6866786c"

# ===============================
# 공공 API URL
# ===============================

# 기상청 단기예보 API
WEATHER_BASE_URL = (
    "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
)

# 서울시 실시간 교통정보 API
TRAFFIC_BASE_URL =  "http://openapi.seoul.go.kr:8088"


# 서울시 미세먼지/대기환경 API
SEOUL_AIR_BASE_URL = "http://openapi.seoul.go.kr:8088"

# 지하철 API 키
SUBWAY_BASE_URL = "http://swopenAPI.seoul.go.kr/api/subway"

# ===============================
# Oracle DB 설정
# ===============================

ORACLE_HOST = "localhost"
ORACLE_PORT = 1521
ORACLE_SID = "xe"
ORACLE_USER = "project"
ORACLE_PASSWORD = "1234"

# ===============================
# 공통 설정
# ===============================

# API 호출 타임아웃 (초)
REQUEST_TIMEOUT = 10
