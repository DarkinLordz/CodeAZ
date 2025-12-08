import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_DIR = os.path.join(ROOT_DIR, "config")
DATA_DIR = os.path.join(ROOT_DIR, "data")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
SRC_DIR = os.path.join(ROOT_DIR, "src")

CONFIG_JSON = os.path.join(CONFIG_DIR, "config.json")
XP_JSON = os.path.join(DATA_DIR, "xp.json")

SYSTEM_LOG = os.path.join(LOGS_DIR, "system.log")