import logging
import aiohttp
from datetime import timedelta
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=60)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    api_key = config.get("api_key")
    station = config.get("station", "부개")
    if not api_key:
        return
    async_add_entities([SubwaySensor(api_key, station)], True)

class SubwaySensor(Entity):
    def __init__(self, api_key, station):
        self._api_key = api_key
        self._station = station
        self._state = "로딩 중"
        self._attributes = {}
        self._attr_unique_id = f"jihaceol_{station}"
        self._attr_name = f"지하철 도착 정보 ({station})"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        """HA 엔티티 속성에 상행/하행별 정리된 정보 표출"""
        return self._attributes

    async def async_update(self):
        url = f"http://swopenAPI.seoul.go.kr/api/subway/{self._api_key}/json/realtimeStationArrival/1/4/{self._station}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        arrivals = data.get("realtimeArrivalList", [])
                        
                        if arrivals:
                            # 1. 원본 전체 리스트 저장
                            self._attributes["realtimeArrivalList"] = arrivals
                            
                            # 2. 상행선 데이터만 추출
                            up_trains = [t for t in arrivals if t.get("updnLine") == "상행"]
                            
                            if up_trains:
                                # 메인 State는 첫 번째 상행 열차 메시지
                                self._state = up_trains[0].get("arvlMsg2", " 정보 없음")
                                
                                # 첫 번째 상행 열차 속성
                                self._attributes["up_1st_line"] = up_trains[0].get("trainLineNm", "")
                                self._attributes["up_1st_msg"] = up_trains[0].get("arvlMsg2", "")
                                
                                # 두 번째 상행 열차가 있을 경우 속성 추가
                                if len(up_trains) > 1:
                                    self._attributes["up_2nd_line"] = up_trains[1].get("trainLineNm", "")
                                    self._attributes["up_2nd_msg"] = up_trains[1].get("arvlMsg2", "")
                                else:
                                    self._attributes["up_2nd_line"] = ""
                                    self._attributes["up_2nd_msg"] = "다음 열차 없음"
                            else:
                                self._state = "상행 열차 없음"
                        else:
                            self._state = "운행 정보 없음"
                    else:
                        self._state = f"API Error ({response.status})"
        except Exception as e:
            _LOGGER.error(f"API 요청 실패: {e}")
            self._state = "연결 오류"