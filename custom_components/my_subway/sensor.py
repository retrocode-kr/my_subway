import requests
from datetime import timedelta
from homeassistant.helpers.entity import Entity

SCAN_INTERVAL = timedelta(seconds=60) # 60초마다 API 호출

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the subway sensor platform."""
    api_key = config.get("api_key")
    station = config.get("station", "부개")
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
            data = response.json()
            self._state = data['realtimeArrivalList'][0]['arvlMsg2']
        except Exception:
            self._state = "Error"