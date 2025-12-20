import os

# Keeping the names of directories in variables
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# os.path.abspath(__file__) gets the current file
# os.path.dirname gets the parent directory - src 
# we do that again to get our projects "root" directory

# all these lines do the same thing, 

CONFIG_DIR = os.path.join(ROOT_DIR, "config") # this for example creates "CodeAZ-BOT/config"
DATA_DIR = os.path.join(ROOT_DIR, "data") # and so on.
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
SRC_DIR = os.path.join(ROOT_DIR, "src")

CONFIG_JSON = os.path.join(CONFIG_DIR, "config.json") # Gets the path of the config json (config + / + config.json)
XP_JSON = os.path.join(DATA_DIR, "xp.json") # same thing

SYSTEM_LOG = os.path.join(LOGS_DIR, "system.log") # system logs are located in LOGS_DIR\system.log