import start
import logwrite
import gps
import img_dtc
import WeakFMEmitter
import motor
import camera2

import time
from enum import Enum
import sys
import _thread

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
mv = motor.Motor()
img = img_dtc.ImageDetection()
cm = camera2.Camera()

flag = False

def stop_reqest():
    global flag
    finish_time = time.time() + (18 * 60)#強制終了
    while True:
        if(time.time()>=finish_time):
            flag = True
            _thread.interrupt_main()
        time.sleep(1)

def main():
    cnt = 0
    try:
        fm.transmitFMMessage("taikityu-")
        condition = Status.WAIT.value
        log.write(condition,"INFO")
        start.awaiting()

        _thread.start_new_thread(stop_reqest, ())# 強制終了命令を待機

        condition = Status.START.value
        fm.transmitFMMessage("ugokidasuyo-")
        log.write(condition,"INFO")

        condition = Status.LOCATIONPhase.value
        gps.main(mv=mv)

        condition = Status.CAMERAPhase.value
        log.write(condition,"INFO")
        while True:
            im = cm.cap(cnt)
            direct = img.red_mask(im,cnt)
            if direct == "goal":
                mv.move("forward",5)
                condition = Status.GOAL.value
                break
            elif direct == "search":
                fm.transmitFMMessage("sagashitemasu")
                mv.move(direct,0.5)
            else:
                fm.transmitFMMessage(direct+"nisusumimasu")
                mv.move(direct,1)
            cnt += 1
        log.write(condition,"INFO")

        fm.transmitFMMessage("go-rusimasita")
    except KeyboardInterrupt:
        if flag:
            log.write("強制終了-タイムアウト","INFO")
        else:
            log.write("KeyboardInterrupt","INFO")
    except SystemExit:
        if flag:
            log.write("SystemExit-強制終了","INFO")
        else:
            log.write("SystemExit","WARNING")
    finally:
        mv.cleanup()
    
if __name__ =="__main__":
    main()
