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
from typing import Dict

# 状態制御クラス
class Status(Enum):
    WAIT = "waiting"
    START = "start"
    LOCATIONPhase = "search_with_GPS"
    CAMERAPhase = "search_with_CAMERA"
    GOAL = "GOAL"

#オブジェクトの生成
log = logwrite.MyLogging()
fm = WeakFMEmitter.FMemitter()
gps = gpsnew.GPSModule()
config = configloading.Config_reader()

#各モジュールの初期化
start.init()
gps.connect()
mv = motor.Motor()
img = img_dtc.ImageDetection()
try:
    cm = camera2.Camera()
except Exception as e:
    log.write(e,"ERROR")

#大域変数の設定
GOAL = {"lat":config.reader("GOAL","lat","float"),"lon":config.reader("GOAL","lon","float")}
Initial_Destination = {"lat":GOAL["lat"],"lon":GOAL["lon"]-0.000200}#西に20mずらす
FLAG = False

def stop_reqest():
    global FLAG
    finish_time = time.time() + (18 * 60)#強制終了
    while True:
        if(time.time()>=finish_time):
            FLAG = True
            _thread.interrupt_main()
        time.sleep(5)

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

        # # GPSフェーズ
        condition = Status.LOCATIONPhase.value
        #初期位置の決定
        while True:
            try:
                log.write("waiting for catching GPS-Date","DEBUG")
                lat, lon, satellites, utc_time, dop = gps.get_gps_data()
                if (lat is not None and lon is not None):
                    break
            except KeyboardInterrupt:
                break
            time.sleep(0.5)
        log.write(f"Latitude:{lat},Longitude:{lon},Satellites:{satellites},Time:{utc_time},DOP{dop}","INFO")
        logwrite.forCSV(lat,lon)
        current_coordinate = {"lat":lat,"lon":lon}
        mv.move("forward",7)

        #初期目標地点へ接近開始
        current_coordinate = gps_movement(Initial_Destination,current_coordinate,5)
        #ゴール座標への接近開始
        _ = gps_movement(GOAL,current_coordinate,8)

        #画像処理フェーズ
        condition = Status.CAMERAPhase.value
        log.write(condition,"INFO")
        while True:
            im = cm.cap(cnt)
            if im is not None:
                direct = img.red_mask(im,cnt)
                if direct == "goal":
                    mv.move("forward",5,duty=80)
                    condition = Status.GOAL.value
                    break
                elif direct == "search":
                    fm.transmitFMMessage("sagashitemasu")
                    mv.move(direct,0.5,duty=50)
                else:
                    fm.transmitFMMessage("mituketa")
                    if direct == "forward":
                        mv.move(direct,4,duty=50)
                    else:
                        mv.move(direct,0.5,duty=50)
                cnt += 1
            else:
                fm.transmitFMMessage("satuedekinaiyo!")
        log.write(condition,"INFO")

        fm.transmitFMMessage("go-rusimasita")
    except KeyboardInterrupt:
        if FLAG:
            log.write("Forced Termination-TimeOut","INFO")
        else:
            log.write("KeyboardInterrupt","INFO")
    except SystemExit:
        if FLAG:
            log.write("SystemExit-Forced Termination","INFO")
        else:
            log.write("SystemExit","WARNING")
    except Exception as e:
        log.write(e,"ERROR")
    finally:
        log.write("All phase was finished.","INFO")
        mv.cleanup()
        gps.disconnect()
        cm.disconnect()
    
def gps_movement(target:Dict[float,float],current_coordinate:Dict[float,float],TARGET_DISTANCE) -> dict[float,float]:
    while True:
        previous_coordinate = current_coordinate.copy()
        while True:
            try:
                log.write("waiting for catching GPS-Date","DEBUG")
                lat, lon, satellites, utc_time, dop = gps.get_gps_data()
                if gpsnew.cheak_data(lat,lon,previous_coordinate):
                    break
                else:
                    log.write("Reacquisition","INFO")
            except KeyboardInterrupt:
                break
            time.sleep(0.5)
        log.write(f"Latitude:{lat},Longitude:{lon},Satellites:{satellites},Time:{utc_time},DOP{dop}","INFO")
        logwrite.forCSV(lat,lon)
        current_coordinate = {"lat":lat,"lon":lon}

        log.write(f"previous_coordinate:{previous_coordinate},current_coordinate{current_coordinate}","DEBUG")

        result = gpsnew.calculate_target_distance_angle(current_coordinate,previous_coordinate,target,TARGET_DISTANCE)
        log.write(f"Distance:{result['distance']},Degree:{result['deg']}","INFO")
        if (result["dir"] != "Immediate"):
            if result["dir"] == "forward":
                fm.transmitFMMessage("zensin")
            elif result["dir"] == "left":
                fm.transmitFMMessage("hidari")
                mv.move("left",4*(-result["deg"])/180)
            else:
                fm.transmitFMMessage("migi")
                mv.move("right",4*(result["deg"])/180)
            mv.move("forward",15)
        else:
            return current_coordinate

if __name__ =="__main__":
    main()
