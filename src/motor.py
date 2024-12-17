import RPi.GPIO as GPIO
import time
import configparser

class Motor():
    def __init__(self,config):
        self.config = config
        self.duty = int(self.config['MOTER'].get('duty'))
        self.right_pwm = int(self.config['MOTER'].get('right_pwm'))
        self.left_pwm = int(self.config['MOTER'].get('left_pwm'))
        self.right_phase = int(self.config['MOTER'].get('right_ph'))
        self.left_phase = int(self.config['MOTER'].get('left_ph'))

        GPIO.setmode(GPIO.BCM)#setmodeでBCMを用いて指定することを宣言　#GPIOピン番号のこと！

        self.setup_gpio()

        self.initialize_motors()

    def setup_gpio(self):
        GPIO.setup(self.right_pwm,GPIO.OUT)#PWM出力
        GPIO.setup(self.right_phase,GPIO.OUT)#デジタル出力
        GPIO.setup(self.left_pwm,GPIO.OUT)#PWM出力
        GPIO.setup(self.left_phase,GPIO.OUT)#デジタル出力

    def initialize_motors(self):
        self.right = GPIO.PWM(self.right_pwm,200)
        self.left = GPIO.PWM(self.left_pwm,200)
        # GPIO.output(self.right_phase,GPIO.HIGH)
        # GPIO.output(self.left_phase,GPIO.HIGH)
        self.right.start(0)
        self.left.start(0)

    def move(self,direction,moter_active_time):
        self.adjust_duty_cycle(direction)

        stop_time = time.time() + moter_active_time
        while time.time() < stop_time:
            self.right.ChangeDutyCycle(self.right_duty)
            self.left.ChangeDutyCycle(self.left_duty)

        self.right.ChangeDutyCycle(0)
        self.left.ChangeDutyCycle(0)

    def adjust_duty_cycle(self,direction):
        GPIO.output(self.right_phase,GPIO.HIGH)
        GPIO.output(self.left_phase,GPIO.HIGH)
        if direction == "forward":
            self.right_duty = self.left_duty = self.duty
        elif direction == "right":
            self.right_duty = self.duty * 0.6
            self.left_duty = self.duty
        elif direction == "left":
            self.right_duty = self.duty
            self.left_duty = self.duty * 0.6
        else:
            self.right_duty = self.left_duty = self.duty
            GPIO.output(self.right_phase,GPIO.LOW)
            GPIO.output(self.left_phase,GPIO.LOW)
        
    def cleanup(self):
        GPIO.cleanup()

def main():
    #ConfigParserオブジェクトを生成
    config = configparser.ConfigParser()

    #設定ファイル読み込み
    config.read("cansat_config.ini")
    motor = Motor(config)
    print("forward,right,left")
    try:
        while True:
            direction =input("direction:")
            motor.move(direction,3)
    except KeyboardInterrupt:
        motor.cleanup()

if __name__ == "__main__":
    main()