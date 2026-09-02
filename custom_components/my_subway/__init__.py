"""The My Subway Arrival integration."""
import logging

_LOGGER = logging.getLogger(__name__)
_LOGGER.warning("MY_SUBWAY V2 LOADED - unique_id=%s", self._attr_unique_id)
DOMAIN = "my_subway"

def setup(hass, config):
    """Set up the component."""
    return True