from path import SYSTEM_LOG
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(module)s.%(funcName)s: %(message)s",
    handlers=[
        logging.FileHandler(SYSTEM_LOG, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("CodeAZ-BOT")