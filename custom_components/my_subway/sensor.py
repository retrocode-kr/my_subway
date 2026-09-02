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
        self._extra_attributes = {}
        self._attr_unique_id = f"my_subway_{station}"
        self._attr_name = f"지하철 도착 정보 ({station})"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._extra_attributes

    async def async_update(self):
        url = f"http://swopenAPI.seoul.go.kr/api/subway/{self._api_key}/json/realtimeStationArrival/1/4/{self._station}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        arrivals = data.get("realtimeArrivalList", [])
                        
                        attrs = {}
                        if arrivals:
                            attrs["realtimeArrivalList"] = arrivals
                            
                            # '상행' 이면서 btrainSttus가 '일반'인 열차만 필터링
                            up_trains = [
                                t for t in arrivals 
                                if t.get("updnLine") == "상행" and t.get("btrainSttus") == "일반"
                            ]
                            
                            if up_trains:
                                self._state = up_trains[0].get("arvlMsg2", "정보 없음")
                                attrs["up_1st_line"] = up_trains[0].get("trainLineNm", "")
                                attrs["up_1st_msg"] = up_trains[0].get("arvlMsg2", "")
                                
                                if len(up_trains) > 1:
                                    attrs["up_2nd_line"] = up_trains[1].get("trainLineNm", "")
                                    attrs["up_2nd_msg"] = up_trains[1].get("arvlMsg2", "")
                                else:
                                    attrs["up_2nd_line"] = ""
                                    attrs["up_2nd_msg"] = "다음 열차 없음"
                            else:
                                self._state = "상행 일반 열차 없음"
                        else:
                            self._state = "운행 정보 없음"
                            
                        self._extra_attributes = attrs
                    else:
                        self._state = f"API Error ({response.status})"
        except Exception as e:
            _LOGGER.error(f"API 요청 실패: {e}")
            self._state = "연결 오류"