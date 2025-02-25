import start
import logwrite
import gpsnew
import img_dtc
import WeakFMEmitter
import motor
import camera2
import configloading

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
gps = gpsnew.GPSModule()
config = configloading.Config_reader()

start.init()
gps.connect()
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
        #GPSフェーズ
        condition = Status.LOCATIONPhase.value
        goal = {"lat":config.reader("GOAL","lat","intenger"),"lon":config.reader("GOAL","lon","intenger")}#目標座標の読み込み
        lat, lon, satellites, utc_time, dop = gps.get_gps_data()
        log.write(f"Latitude:{lat},Longitude:{lon},Satellites:{satellites},Time:{utc_time},DOP{dop}","INFO")
        current_coordinate = {"lat":lat,"lon":lon}
        mv.move("forward",7)
        while True:
            previous_coordinate = current_coordinate
            lat, lon, satellites, utc_time, dop = gps.get_gps_data()
            log.write(f"Latitude:{lat},Longitude:{lon},Satellites:{satellites},Time:{utc_time},DOP{dop}","INFO")
            current_coordinate = {"lat":lat,"lon":lon}
            result = gps.calculate_target_distance_angle(current_coordinate,previous_coordinate,goal)
            if (result["dir"] != "Immediate"):
                if result["dir"] == "forward":
                    pass
                elif result["dir"] == "left":
                    mv.move("left",4*(-result["deg"])/180)
                else:
                    mv.move("left",4*(-result["deg"])/180)
                mt.move("forward",10)
            else:
                break
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
        gps.disconnect()
    
if __name__ =="__main__":
    main()
