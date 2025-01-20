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
    WAIT = "waiting"
    START = "start"
    LOCATIONPhase = "search_with_GPS"
    CAMERAPhase = "search_with_CAMERA"
    GOAL = "GOAL"

log = logwrite.MyLogging()
fm = WeakFMEmitter.FMemitter()
start.init()
gps.init()

flag = False

def stop_reqest():
    global flag
    finish_time = time.time() + (18 * 60)#強制終了
    while True:
        if(time.time()>=finish_time):
            flag = True
            thread.interrupt_main()
        time.sleep(1)

def main():
    try:
        fm.stringToAscii("taikityu-")
        condition = Status.WAIT.value
        log.write(condition,"INFO")
        start.awaiting()

        thread.start_new_thread(stop_reqest, ())# 強制終了命令を待機

        condition = Status.START.value
        fm.stringToAscii("ugokidasuyo-")
        log.write(condition,"INFO")

        condition = Status.LOCATIONPhase.value
        gps.main()

        condition = Status.CAMERAPhase.value
        log.write(condition,"INFO")
        img_dtc.main()
        condition = Status.GOAL.value
        log.write(condition,"INFO")

        fm.stringToAscii("go-rusimasita")
    except KeyboardInterrupt:
        if flag:
            log.write("強制終了","INFO")
        else:
            print("KeyboardInterrupt")
    except SystemExit:
        printf("強制終了させました")
    finally:
        pass
    
if __name__ =="__main__":
    main()