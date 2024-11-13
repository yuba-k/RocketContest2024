from picamera2 import Picamera2
import cv2

class Camera():
    def __init__(self):
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_still_configuration(main={"format":"RGB888","size":(640,480)}))
    def cap(self):
        self.picam.start()
        im = self.picam.capture_array()
        self.save(im)
    def save(self,im):
        cv2.imwrite("test_cv2.jpg",im)

def main():
    camera = Camera()
    camera.cap()

if __name__ == "__main__":
    main()