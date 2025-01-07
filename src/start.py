# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import logwrite
import configloading

config = configloading.Config_reader()
st_pin = config.reader("start","st_pin","intenger")
def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(st_pin, GPIO.IN)

def awaiting():
    log = logwrite.MyLogging()
    while(True):
        value = GPIO.input(st_pin)
        print(value)
        if(value == 0):
            log.write("program start","INFO")
            break
        time.sleep(1)
    time.sleep(30)#パラシュート展開後待機時間
    return
