from picamera2 import Picamera2
import cv2
import numpy as np

import configloading
import logwrite

class Camera():
    def __init__(self):
        config = configloading.Config_reader()
        height = config.reader("camera","height","intenger")
        weight = config.reader("camera","weight","intenger")
        log = logwrite.MyLogging()
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_still_configuration(main={"format":"RGB888","size":(weight,height)}))
    def cap(self,cnt):
        self.picam.start()
        im = self.picam.capture_array()
        im = np.flipud(im)
        im = np.fliplr(im)
        self.save(im,cnt)
        return im
    def save(self,im,cnt):
        cv2.imwrite(f"../img/default/{cnt}test_cv2.jpg",im)

def main():
    camera = Camera()
    camera.cap()

if __name__ == "__main__":
    main()