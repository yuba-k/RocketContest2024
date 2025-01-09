import start
import logwrite
import gps
import img_dtc
import WeakFMEmitter

import time
from enum import Enum
import sys
import thread

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

def stop_reqest():
    finish_time = time.time() + (18 * 60)#強制終了
    while True:
        if(time.time()>=finish_time):
            thread.interrupt_main()
        time.sleep(1)

def main():
    try:
        fm.stringToAscii("taikityu-")
        condition = Status.WAIT
        log.write(condition,"INFO")
        start.awaiting()

        condition = Status.START
        fm.stringToAscii("ugokidasuyo-")
        log.write(condition,"INFO")

        thread.start_new_thread(stop_reqest, ())# 強制終了指示を待機

        condition = Status.LOCATIONPhase
        gps.main()

        condition = Status.CAMERAPhase
        log.write(condition,"INFO")
        img_dtc.main()
        log.write(condition,"INFO")

        fm.stringToAscii("go-rusimasita")
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except SystemExit:
        printf("強制終了させました")
    
if __name__ =="__main__":
    main()