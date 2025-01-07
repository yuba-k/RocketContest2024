import start
import logwrite
import gps

from enum import Enum

class Status(Enum):
    WAIT = "waiting_start"
    START = "start"
    LOCATIONPhase = "search_with_GPS"
    CAMERAPhase = "search_with_CAMERA"
    GOAL = "GOAL"

log = logwrite.MyLogging()
start.init()
gps.init()

def main():
    condition = Status.WAIT
    log.write(condition,"INFO")
    start.awaiting()

    condition = Status.START
    log.write(condition,"INFO")

    condition = Status.LOCATIONPhase
    gps.main()
    
if __name__ =="__main__":
    main()