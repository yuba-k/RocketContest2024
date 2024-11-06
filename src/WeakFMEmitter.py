import smbus
import time

i2c = smbus.SMBus(1)
addr = 0x2e 

#

def stringToAscii(message):
    string = [int(hex(ord(s)),0) for s in message]
    return string

def sendDataViaI2C(string):
    i2c.write_i2c_block_data(addr,0,string)
    i2c.write_byte_data(addr,0,0x0d)#終了コード
    time.sleep(5)

def transmitFMMessage(message):
    string = stringToAscii(message)
    sendDataViaI2C(string)

def main():
    while(True):
        string = input(">>>")
        transmitFMMessage(string)

if __name__ == "__main__":
    main()