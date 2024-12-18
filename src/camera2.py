from picamera2 import Picamera2
import cv2

import configloading

class Camera():
    def __init__(self):
        config = configloading.Config_reader()
        height = config.reader("camera","height","intenger")
        weight = config.reader("camera","weight","intenger")
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_still_configuration(main={"format":"RGB888","size":(weight,height)}))
    def cap(self):
        self.picam.start()
        im = self.picam.capture_array()
        self.save(im)
        return im
    def save(self,im):
        cv2.imwrite("../img/default/test_cv2.jpg",im)

def main():
    camera = Camera()
    camera.cap()

if __name__ == "__main__":
    main()