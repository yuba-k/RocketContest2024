import cv2
import numpy as np

class Detection():
    def __init__(self):
        self.file_path = "../img/default/"
        self.file_list = ["50", "75", "100", "150", "200", "250", "300", "350", "400", "450", "500", "1000"]
        self.img = []
        self.mask_red = []
        self.result_img = []
        self.contours = []
        self.output = []
        self.bound_lower = np.array([90, 100, 100])
        self.bound_upper = np.array([120, 255, 255])
        self.read()
        self.red_detection()
        self.save()

    def read(self):
        for num in self.file_list:
            self.img.append(cv2.imread(self.file_path + num + "cm.jpg"))  # 元のBGR画像を読み込む

    def red_detection(self):
        for i, img in enumerate(self.img):
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # BGRからHSVに変換
            mask = cv2.inRange(hsv, self.bound_lower, self.bound_upper)
            kernel = np.ones((7, 7), np.uint8)
            mask_red = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)  # 変数を上書き

            self.result_img.append(cv2.bitwise_and(img, img, mask=mask_red))  # 元の画像を使う
            contours, _ = cv2.findContours(mask_red.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.output.append(cv2.drawContours(self.result_img[i], contours, -1, (255, 0, 0), 3))

    def save(self):
        for i, img in enumerate(self.output):
            cv2.imwrite(f"../img/result/{i}.jpg", img)

def main():
    Detection()

if __name__ == "__main__":
    main()
