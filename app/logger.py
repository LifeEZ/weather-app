import logging
import sys

from pythonjsonlogger.json import JsonFormatter

logger = logging.getLogger("weather_app")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter("%(message)s"))
logger.addHandler(handler)
