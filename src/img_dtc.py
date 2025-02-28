import cv2
import numpy as np
import math
import configloading
# import camera2
# import motor

class ImageDetection():
    def __init__(self):
        config = configloading.Config_reader()

        self.height = config.reader("camera", "height", "intenger")
        self.width = config.reader("camera", "weight", "intenger")

    def red_mask(self,img,cnt):
        self.img = to_convert_HDR(img)

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

        return self.opening(masked_img,cnt)

    def opening(self,img,cnt):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        _,img = cv2.threshold(gray,0,255,cv2.THRESH_OTSU)# 入力画像（グレースケール画像を指定すること）# 閾値 # 閾値を超えた画素に割り当てる値# 閾値処理方法
        neiborhood = np.array([[0, 1, 0],[1, 1, 1],[0, 1, 0]],np.uint8)
        # 収縮
        img_erode = cv2.erode(img,neiborhood,iterations=3)
        # 膨張
        img_dilate = cv2.dilate(img_erode,neiborhood,iterations=3)
        cv2.imwrite("../img/result/opening.jpg",img_dilate)
        img = self.filter(img_dilate)
        if img is None:
            return "search"
        return self.get_target_point(img,cnt)

    def filter(self,img):
        contours,_= cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
        # 小さい輪郭は誤検出として削除する
        contours = list(filter(lambda x: cv2.contourArea(x) > 1000, contours))
        # 一番面積が大きい輪郭を選択する。
        if not contours or all(cv2.contourArea(x) == 0 for x in contours):
            return None
        else:
            print("not empty")
            max_cnt = max(contours, key=lambda x: cv2.contourArea(x))
        # 黒い画像に一番大きい輪郭だけ塗りつぶして描画する
        out = np.zeros_like(img)
        cv2.drawContours(img, [max_cnt], -1, color=255, thickness=-1)
        return img

    def get_target_point(self,img,cnt):
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
        coordinates_y["left"] = abs(int(self.height) - temp[1][0])
        img = rorate_img(img)
        img = rorate_img(img)

        temp = list(temp)
        temp.clear()
        temp = get_coordinates(img)
        coordinates_x["right"] = abs(int(self.width) - temp[0][0])
        coordinates_y["right"] = temp[1][0]
        img = rorate_img(img)

        cv2.line(img,(coordinates_x["top"],coordinates_y["top"]),(coordinates_x["right"],coordinates_y["right"]),(100,0,0),thickness=10,lineType=cv2.LINE_8,shift=0)
        cv2.imwrite("../img/result/line_1.jpg",img)
        cv2.line(img,(coordinates_x["right"],coordinates_y["right"]),(coordinates_x["left"],coordinates_y["left"]),(100,0,0),thickness=10,lineType=cv2.LINE_8,shift=0)
        cv2.imwrite("../img/result/line_2.jpg",img)
        cv2.line(img,(coordinates_x["left"],coordinates_y["left"]),(coordinates_x["top"],coordinates_y["top"]),(100,0,0),thickness=10,lineType=cv2.LINE_8,shift=0)

        for i,j in coordinates_x.items():
            print(f"{i}_x:{j}")
        for i,j in coordinates_y.items():
            print(f"{i}_y:{j}")

        cv2.imwrite(f"../img/result/{cnt}result.jpg",img)

        if  (abs(coordinates_x["left"] - coordinates_x["right"]))>=self.width*0.8:
            return "goal"
        return self.get_center_point(coordinates_x["left"],coordinates_x["right"],coordinates_x["top"])

    def get_center_point(self,right,left,top):
        result = ((right+left)/2 + top)//2
        if result < self.width//3:
            return "left"
        elif result < self.width//3*2:
            return "forward"
        else:
            return "right"

def bgr_to_hsv(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

def get_coordinates(img):
    white_pixels = np.where(img == 255)
    return white_pixels

def rorate_img(img):
    return cv2.rotate(img,cv2.ROTATE_90_CLOCKWISE)

def bgr_to_lab(img):
    return cv2.cvtColor(img,cv2.COLOR_BGR2LAB)

def gamma_correction(img,gm):
    lab = bgr_to_lab(img)#変換
    l,a,b = cv2.split(lab)

    mean_intensity = np.mean(l)
    gamma = math.log(mean_intensity/255.0)/math.log(gm/255.0)
    invGamma = 1.0/gamma
    table = np.array([((i/255.0)**invGamma)*255 for i in np.arange(256)]).astype("uint8")
    afImage = cv2.LUT(l,table)

    lab_correveted = cv2.merge((afImage,a,b))

    afImage = cv2.cvtColor(lab_correveted,cv2.COLOR_LAB2BGR)

    return afImage

def to_convert_HDR(img):
    afimg = []
    for gm in [5,147,200]:
        afimg.append(gamma_correction(img,gm))
    merge_mertens = cv2.createMergeMertens()
    res_mertens = merge_mertens.process(afimg)
    res_mertens_8bit = np.clip(res_mertens*255, 0, 255).astype('uint8')
    return res_mertens_8bit

def main():
    # img_detection = ImageDetection()
    # cam = camera2.Camera()
    # mt = motor.Motor()
    # cnt = 0#カウンタ
    # while True:
    #     img = cam.cap(cnt)
    #     if(img == "PICAMERA-ERROR"):
    #         return "ERROR"
    #     detc = img_detection.red_mask(img,cnt)
    #     if(detc == "goal"):
    #         mt.move("forward",2)
    #         break
    #     mt.move(detc,0.5)
    #     cnt += 1
    imgDetc = ImageDetection()
    for i in range(1,38):
        img = cv2.imread(f"../img/backlight_selection/file({i}).jpg")
        img = cv2.resize(img,dsize = (640,460))
        imgDetc.red_mask(img,i)

if __name__ == "__main__":
    main()