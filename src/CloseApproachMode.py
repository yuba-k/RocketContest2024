import camera2
import img_dtc
import motor

def main():
    camera = camera2.Camera()
    imgdetect = img_dtc.ImageDetection()
    mt = motor.Motor()

    while True:
        img = camera.cap()
        result_direction = imgdetect.red_mask(img)
        mt.move(result_direction,1.5)

if __name__ == "__main__":
    main()