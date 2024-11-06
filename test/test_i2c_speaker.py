import smbus
import time

i2c = smbus.SMBus(1)
addr = 0x2e 

def conversion():
#    message = input(">>>")
    message = "konnichiwa."
    string = [int(hex(ord(s)),0) for s in message]
    return string

while(True):
    string = conversion()
    i2c.write_i2c_block_data(addr,0,string)
    i2c.write_byte_data(addr,0,0x0d)
    time.sleep(5)