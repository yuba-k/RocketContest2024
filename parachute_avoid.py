import cv2
import numpy as np

import camera2

# 黒色は２つの領域にまたがります！！
# np.array([色彩, 彩度, 明度])
# 各値は適宜設定する！！
LOW_COLOR1 = np.array([0,0,0]) # 各最小値を指定
HIGH_COLOR1 = np.array([180, 255, 90]) # 各最大値を指定
cam = camera2.Camera()

def Clahe():
    img = cam.cap(cnt = 0)#cv2.imread(img_name) # 画像を読み込む
    img_resize = cv2.resize(img, (960,540 ))    #フルHDの半分
    #img_resizse = cv2.resize(img, (1920,1080 )) #フルHD
    img_resize=img_resize[270:540, 0:960]       #下半分だけにトリミング
    img_blur = cv2.blur(img_resize, (5, 5))
    img_yuv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2YUV) # RGB => YUV(YCbCr)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)) # claheオブジェクトを生成
    img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0]) # 輝度にのみヒストグラム平坦化
    img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR) # YUV => RGB
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) # BGRからHSVに変換
    
    bin_img1 = cv2.inRange(hsv, LOW_COLOR1, HIGH_COLOR1) # マスクを作成

    num_labels,label_img, stats, centroids = cv2.connectedComponentsWithStats(bin_img1) # 連結成分でラベリングする
    #背景のラベルを削除
    num_labels = num_labels - 1
    stats = np.delete(stats, 0, 0)
    centroids = np.delete(centroids, 0, 0)
    masked_img = cv2.bitwise_and(img, img, mask= bin_img1)

    if num_labels >= 1:  #ラベルの有無で場合分け
        threshold_area = 960 * 270 * 0.10  #下半分の総面積(px)の10%
        total_area=0
        for i in range(0, num_labels):
             total_area += stats[i, cv2.CC_STAT_AREA]
        print(total_area)

        if total_area >= threshold_area:
            cv2.imwrite("//home//pi//img//2.jpg",masked_img)
            return 1
        else:
            cv2.imwrite("//home//pi//img//2.jpg",masked_img)
            return 0
    else:
        cv2.imwrite("//home//pi//img//2.jpg",masked_img)
        return 0
if __name__=="__main__":
    print("start")
    result=Clahe()
    print(result)
    print("finish")