import time
import math
import serial
import adafruit_gps
import sys
import RPi.GPIO as GPIO
import logwrite
import signal
import configloading

def main(mv):
    log = logwrite.MyLogging()
    sec = 10
    duty = 80
    
    #ゴールの座標をここに入力！
    coordinate_goal = {'lat':30.374266, 'lon':130.960020}
    log.write(f"coordinate_goal:{coordinate_goal}","INFO")

    coordinate_new = get_gpsdata()
    while not gps.has_fix:  #GPSデータの取得待ち...     Loading...
        print("Waiting for fix...")
        time.sleep(1)
        coordinate_new = get_gpsdata()
    log.write(f"{coordinate_new}","INFO")
    mv.move("straight" , sec, duty=75) #とりあえずsec秒前進．前へすすめー！
    while True:
        try:
            coordinate_old = coordinate_new
            coordinate_new = get_gpsdata()
            while(coordinate_old['lat'] == coordinate_new['lat'] and
            coordinate_old['lon'] == coordinate_new['lon']):
                coordinate_new = get_gpsdata()  #前回と今回のGPSデータが同一だった場合，新規取得
            log.write(f"現在座標:{coordinate_new}","INFO")
            
            if not gps.has_fix or coordinate_new['lat'] is None:
                print("Waiting for fix...")
                continue
            
            #以下，北を0度として考える．
            #ゴールと機体の位置を結ぶベクトルの角度を計算する．西がマイナス，東がプラス
            coordinate_diff_goal = { 'lat' : (coordinate_goal['lat'] - coordinate_new['lat']), 
                                'lon' : (coordinate_goal['lon'] - coordinate_new['lon'])}
            degree_for_goal = math.atan2(
                    coordinate_diff_goal['lon'], coordinate_diff_goal['lat']) / math.pi * 180
            
            #機体が動いた経路の角度を計算する．
            #TODO GPSデータに移動経路の方角が含まれている？ 要検証
            coordinate_diff_me = { 'lat' : (coordinate_new['lat'] - coordinate_old['lat']), 
                                'lon' : (coordinate_new['lon'] - coordinate_old['lon'])}
            degree_for_me = math.atan2(
                    coordinate_diff_me['lon'], coordinate_diff_me['lat']) / math.pi * 180
            
            #ゴールの角度から機体が動いた角度を引き，機体から見たゴールの角度を計算する．
            #このとき，機体前方を0度とし，左がマイナス，右がプラス
            degree = degree_for_goal-degree_for_me
            degree = (degree + 360) if (degree < -180) else degree
            degree = (degree - 360) if (180 < degree) else degree

            #目標と現在位置との距離を三平方より導出
            distance=math.sqrt(coordinate_diff_goal['lat']**2+coordinate_diff_goal['lon']**2)
            if distance<=0.00005:
                return 0#距離が0.00005km(5m)以下になったらGPSフェーズ終了
            distance=distance*math.pow (10,5)#[m]
            log.write(f"距離:{distance}m","INFO")
            log.write("角度:" + "{:.3f}".format(degree),"INFO")

            if degree <= -45:
                mv.move("left", 4*(-degree)/180,duty=duty)   #角度が大きければ大きいほど，曲がる量を多く
                mv.move("straight", sec,duty=duty)
            elif degree >= 45:
                mv.move("right", 4*degree/180)
                mv.move("straight", sec, duty=duty)
            else :#+-45
                mv.move("straight", sec, duty=duty)
        except KeyboardInterrupt:
            return
# sample
#            move("right", duty, sec)
#            move("straight", duty, sec)
#            move("left", duty, sec)

def init():
    #GPS initialization
    global uart
    uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=10)
    signal.signal(signal.SIGINT, signal_handler)
    global gps
    gps = adafruit_gps.GPS(uart, debug=False)
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    #GPRMCとGPGGAを取得．
    gps.send_command(b"PMTK220,1000")
    #出力頻度は1000[ms]間隔

def get_gpsdata(): 
    time.sleep(3)
    uart.reset_input_buffer()   #シリアル通信のバッファ消去
    time.sleep(1)
    gps.update()
    return {'lat':gps.latitude, 'lon':gps.longitude}

def signal_handler(sig, frame):
    print("\nExiting the program.")
    sys.exit(0)

if __name__ == '__main__':
    init()
    data = get_gpsdata()
    print(data['lat'], data['lon'])
