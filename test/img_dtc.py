import cv2
import numpy as np
import configloading


class ImageDetection():
    def __init__(self):
        config = configloading.Config_reader()
        self.img = cv2.imread("../img/default/75cm.jpg")
        if self.img is None:
            print("Image not loaded properly.")
            return
        self.height = config.reader("camera", "height", "character")
        self.width = config.reader("camera", "weight", "character")

    def red_mask(self):
        if self.img is None:
            print("Image not loaded properly.")
            return

        # 赤色のHSV範囲
        hsv_min1 = np.array([0, 100, 100])
        hsv_max1 = np.array([10, 255, 255])
        hsv_min2 = np.array([170, 100, 100])
        hsv_max2 = np.array([180, 255, 255])

        # HSVに変換
        hsv_img = bgr_to_hsv(self.img)

        # 2つの赤色範囲をマスク
        mask1 = cv2.inRange(hsv_img, hsv_min1, hsv_max1)
        mask2 = cv2.inRange(hsv_img, hsv_min2, hsv_max2)

        # 2つのマスクを統合
        mask = cv2.bitwise_or(mask1, mask2)

        # マスクを使って画像を抽出
        masked_img = cv2.bitwise_and(self.img, self.img, mask=mask)

        # 結果を保存
        cv2.imwrite("../img/result/masked.jpg", masked_img)
        self.opening(masked_img)

    def opening(self,img):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        _,img = cv2.threshold(gray,0,255,cv2.THRESH_OTSU)# 入力画像（グレースケール画像を指定すること）# 閾値 # 閾値を超えた画素に割り当てる値# 閾値処理方法
        neiborhood = np.array([[0, 1, 0],[1, 1, 1],[0, 1, 0]],np.uint8)
        # 収縮
        img_erode = cv2.erode(img,neiborhood,iterations=10)
        # 膨張
        img_dilate = cv2.dilate(img_erode,neiborhood,iterations=10)
        cv2.imwrite("../img/result/opening.jpg",img_dilate)
        self.get_target_point(img_dilate)

    def get_target_point(self,img):
        coordinates_x = {}
        coordinates_y = {}

        temp = get_coordinates(img)
        coordinates_x["top"] = temp[1][0]
        coordinates_y["top"] = temp[0][0]
        img = rorate_img(img)

        temp = list(temp)
        temp.clear()
        temp = get_coordinates(img)
        coordinates_x["left"] = temp[0][0]
        coordinates_y["left"] = int(self.height) - temp[1][0]
        img = rorate_img(img)
        img = rorate_img(img)

        temp = list(temp)
        temp.clear()
        temp = get_coordinates(img)
        coordinates_x["right"] = int(self.width) - temp[0][0]
        coordinates_y["right"] = temp[1][0]
        img = rorate_img(img)

        cv2.line(img,(coordinates_x["top"],coordinates_y["top"]),(coordinates_x["right"],coordinates_y["right"]),(255,0,0),thickness=10,lineType=cv2.LINE_8,shift=0)
        cv2.line(img,(coordinates_x["right"],coordinates_y["right"]),(coordinates_x["left"],coordinates_y["left"]),(0,255,0),thickness=10,lineType=cv2.LINE_8,shift=0)
        cv2.line(img,(coordinates_x["left"],coordinates_y["left"]),(coordinates_x["top"],coordinates_y["top"]),(0,0,255),thickness=10,lineType=cv2.LINE_8,shift=0)

        cv2.imwrite("result.jpg",img)

def bgr_to_hsv(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

def get_coordinates(img):
    white_pixels = np.where(img)
    return white_pixels

def rorate_img(img):
    return cv2.rotate(img,cv2.ROTATE_90_CLOCKWISE)

def main():
    img_detection = ImageDetection()
    img_detection.red_mask()


if __name__ == "__main__":
    main()
