import start
import logwrite
import gps
import img_dtc
import WeakFMEmitter
import move

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
mv = mote.Motor()

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
        while True:
            direct = img_dtc.red_mask()
            if direct == "goal":
                mt.move("forward",5)
                condition = Status.GOAL.value
                break
            mt.move(direct,2)

        log.write(condition,"INFO")

        fm.stringToAscii("go-rusimasita")
    except KeyboardInterrupt:
        if flag:
            log.write("強制終了-タイムアウト","INFO")
        else:
            log.write("KeyboardInterrupt","INFO")
    finally:
        pass
    
if __name__ =="__main__":
    main()