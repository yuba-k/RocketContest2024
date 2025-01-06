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
    cnt = 0
    while True:
        img = camera.cap(cnt)
        result_direction = imgdetect.red_mask(img,cnt)
        mt.move(result_direction,0.25)
        cnt += 1

if __name__ == "__main__":
    main()