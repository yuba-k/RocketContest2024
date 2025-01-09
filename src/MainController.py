import start
import logwrite
import gps
import img_dtc as imgDetection
import WeakFMEmitter

import time
from enum import Enum

# 状態制御クラス
class Status(Enum):
    WAIT = "waiting_start"
    START = "start"
    LOCATIONPhase = "search_with_GPS"
    CAMERAPhase = "search_with_CAMERA"
    GOAL = "GOAL"

log = logwrite.MyLogging()
fm = WeakFMEmitter.FMemitter()
start.init()
gps.init()

def main():
    try:
        fm.stringToAscii("taikityu-")
        condition = Status.WAIT
        log.write(condition,"INFO")
        start.awaiting()

        condition = Status.START
        fm.stringToAscii("ugokidasuyo-")
        log.write(condition,"INFO")

        start_time = time.time()
        finish_time = time.time() + (18 * 60)#強制終了

        condition = Status.LOCATIONPhase
        gps.main()

        condition = Status.CAMERAPhase
        log.write(condition,"INFO")
        imgDetection.main()
        log.write(condition,"INFO")

        fm.stringToAscii("go-rusimasita")
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    
if __name__ =="__main__":
    main()