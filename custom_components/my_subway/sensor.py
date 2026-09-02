import logging
import requests
from datetime import timedelta
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60) # 60초마다 API 호출

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the subway sensor platform."""
    api_key = config.get("api_key")
    station = config.get("station", "부개")
    if not api_key:
        _LOGGER.error("my_subway: api_key가 설정되지 않았습니다.")
        return
    
    add_entities([SubwaySensor(api_key, station)], True)

class SubwaySensor(Entity):
    def __init__(self, api_key, station):
        self._api_key = api_key
        self._station = station
        self._state = None

    @property
    def name(self):
        return f"지하철 도착 정보 ({self._station})"

    @property
    def state(self):
        return self._state

    def update(self):
        #url = f"http://swopenapi.seoul.go.kr/api/subway/744357696c7073793739527250724d/json/realtimeStationArrival/1/4/%EB%B6%80%EA%B0%9C/"
        url = f"http://swopenapi.seoul.go.kr/api/subway/{self._api_key}/json/realtimeStationArrival/1/4/{self._station}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "realtimeArrivalList" in data and len(data["realtimeArrivalList"]) > 0:
                    # 첫 번째 열차 메시지 추출 (예: "3분 후 도착", "전역 출발")
                    self._state = data["realtimeArrivalList"][0].get("arvlMsg2", "정보 없음")
                else:
                    self._state = "운행 정보 없음"
            else:
                self._state = f"API Error ({response.status_code})"
        except Exception as e:
            _LOGGER.error(f"my_subway: API 호출 중 오류 발생 - {e}")
            self._state = "연결 오류"