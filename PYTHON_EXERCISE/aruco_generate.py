import sys

import cv2 as cv

# 获取预定义的 ArUco 字典 DICT_6X6_250
dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_250)

# 生成 ID 为 23，边长为 200 像素的 ArUco 标记图像
img = cv.aruco.generateImageMarker(dictionary, 23, 400, 1)

if img is None:
    sys.exit("Couldn't generate marker.")

cv.imshow("Display window", img)
key = cv.waitKey(0)

if key == ord('s'):  # 如果按下 's' 键
    # 保存图像
    cv.imwrite("marker23.png", img)