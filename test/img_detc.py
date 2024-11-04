import cv2
import numpy as np
import time

#参考
# https://www.codevace.com/py-opencv-adaptivethreshold/

class Detection():
    def __init__(self, img):
        self.img_default = img
        self.bound_lower = np.array([90, 100, 100])
        self.bound_upper = np.array([120, 255, 255])
        _ , self.width , _ = self.img_default.shape
        print(self.width)

    def color_detection(self):
        hsv = cv2.cvtColor(self.img_default, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.bound_lower, self.bound_upper)
        kernel = np.ones((7, 7), np.uint8)
        mask_color = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask_color = cv2.morphologyEx(mask_color, cv2.MORPH_OPEN, kernel)

        # 元の画像とマスクを合成
        img_result = cv2.bitwise_and(self.img_default, self.img_default, mask=mask_color)

        # 輪郭を描画
        contours, _ = cv2.findContours(mask_color.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        img_contours = cv2.drawContours(np.zeros_like(self.img_default), contours, -1, (0, 0, 255), 10)

        # 元の画像に検出結果を重ねる
        self.img_result = cv2.addWeighted(self.img_default, 0.7, img_result, 0.3, 0)

        # 輪郭を重ねる
        self.img_result = cv2.addWeighted(self.img_result, 1, img_contours, 1, 0)

        #座標導出
        gray = cv2.cvtColor(img_result,cv2.COLOR_BGR2GRAY)
        dst2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV, 11, 20)
        white_pixels = np.where(dst2 == 255)

        self.save()
        return self.adjust_move(white_pixels)

    def adjust_move(self,white_pixels):
        x = white_pixels[1][0]
        print(x)
        if(x < self.width//3):
            return "left"
        elif(self.width//3*2<x):
            return "right"
        else:
            return "forward"

    def save(self):
        cv2.imwrite("../img/result/result.jpg", self.img_result)

def main():
    st = time.time()
    print()
    img_default = cv2.imread("../img/default/200cm.jpg")
    det = Detection(img_default)
    direction = det.color_detection()
    print(direction)
    print(time.time()-st)

if __name__ == "__main__":
    main()
