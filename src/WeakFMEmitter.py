import smbus
import time
import RPi.GPIO

import configloading

class FMemitter():
    def __init__(self):
        config = configloading.Config_reader()
        self.i2c = smbus.SMBus(1)
        self.addr = config.reader("i2c","device_addr","intenger")

    def stringToAscii(self,message):
        string = [int(hex(ord(s)),0) for s in message]
        return string

    def sendDataViaI2C(self,string):
        self.i2c.write_i2c_block_data(self.addr,0,string)
        self.i2c.write_byte_data(self.addr,0,0x0d)#終了コード
        time.sleep(5)

    def transmitFMMessage(self,message):
        string = self.stringToAscii(message)
        self.sendDataViaI2C(string)

def main():
    while(True):
        string = input(">>>")
        fm = FMemitter()
        fm.transmitFMMessage(string)

if __name__ == "__main__":
    main()