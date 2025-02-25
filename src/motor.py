import RPi.GPIO as GPIO
import time
import configloading

import logwrite

class Motor():
    def __init__(self):
        self.config = configloading.Config_reader()
        self.log = logwrite.MyLogging()

        self.duty = self.config.reader("MOTOR","duty","intenger")
        self.right_pwm = self.config.reader("MOTOR","right_pwm","intenger")
        self.left_pwm = self.config.reader("MOTOR","left_pwm","intenger")
        self.right_phase = self.config.reader("MOTOR","right_phase","intenger")
        self.left_phase = self.config.reader("MOTOR","left_phase","intenger")

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

    def move(self,direction,moter_active_time,duty = None):
        if duty == None:
            duty = self.duty
        self.adjust_duty_cycle(direction,duty)

        stop_time = time.time() + moter_active_time
        while time.time() < stop_time:
            self.right.ChangeDutyCycle(self.right_duty)
            self.left.ChangeDutyCycle(self.left_duty)

        self.right.ChangeDutyCycle(0)
        self.left.ChangeDutyCycle(0)

    def adjust_duty_cycle(self,direction,duty):
        GPIO.output(self.right_phase,GPIO.HIGH)
        GPIO.output(self.left_phase,GPIO.HIGH)
        if direction == "forward":
            self.log.write("forward","INFO")
            self.right_duty = duty * 1.1
            self.left_duty = duty
        elif direction == "right" or direction == "search":
            self.log.write("right","INFO")
            self.right_duty = duty * 0.8
            self.left_duty = duty
        elif direction == "left":
            self.log.write("left","INFO")
            self.right_duty = duty * 1.1
            self.left_duty = duty * 0.8
        elif direction == "back":
            self.log.write("back","INFO")
            self.right_duty = self.left_duty = duty
            GPIO.output(self.right_phase,GPIO.LOW)
            GPIO.output(self.left_phase,GPIO.LOW)
        else:
            self.right_duty = self.left_duty = 0
        
    def cleanup(self):
        GPIO.cleanup()

def main():
    motor = Motor()
    print("forward,right,left")
    try:
        while True:
            direction =input("direction:")
            motor.move(direction,3)
    except KeyboardInterrupt:
        motor.cleanup()

if __name__ == "__main__":
    main()
