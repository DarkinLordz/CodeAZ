from path import SYSTEM_LOG # brings the log files path from path.py
import logging # a standart python module

# basically logging settings:
logging.basicConfig(
    level=logging.DEBUG, # logs debug and above debug level, debug is the lowest level
    format="%(asctime)s [%(levelname)s] %(module)s.%(funcName)s: %(message)s", # the format to log in
    handlers=[
        logging.FileHandler(SYSTEM_LOG, encoding="utf-8"), # Send logs to the Log file
        logging.StreamHandler() # Send it to stdout aswell
    ]
)

logger = logging.getLogger("CodeAZ-BOT") # this just gets you a logger and names it "CodeAz-BOT"

"""
    * Better explanation of the formats:
    * asctime -> date&time
    * levelname -> debug type (Debug, Info, etc)
    * module -> module/file name
    * funcName -> name of the function
    * message -> the message passed to the logger
    *
    * %(...)s indicates a logrecord attribure formated as a string, hence the 's'
    * 
"""