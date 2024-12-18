import camera2
import img_dtc
import motor
import logwrite

def main():
    log = logwrite.MyLogging()
    camera = camera2.Camera()
    imgdetect = img_dtc.ImageDetection()
    mt = motor.Motor()

    log.write(loglevel="INFO",logmessage="start")
    while True:
        img = camera.cap()
        result_direction = imgdetect.red_mask(img)
        mt.move(result_direction,1.5)

if __name__ == "__main__":
    main()