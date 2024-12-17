from camera2 import Camera.cap as capture
import img_dtc
import motor

def main():
    imgdetect = img_dtc.ImageDetection()
    motor = motor.Motor

    while True:
        img = capture()
        result_direction = img_dtc.red_mask(img)
        motor.move(result_direction,1.5)

if __name__ == "__main__":
    main()