import numpy as np
import cv2 as cv
import glob

# 终止标准
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# 准备点对象, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((9 * 6, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

# 数组来存储所有图像中的对象点和图像点
obj_points = []  # 真实世界空间中的 3D 点
img_points = []  # 图像平面中的二维点

images = glob.glob('*.png')

print(images.__sizeof__())

# for image in images:
print(1)
img = cv.imread("../../image/22_9x6.png")
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# 找到棋盘角落
ret, corners = cv.findChessboardCorners(gray, (9, 6), None)

# 如果找到,则添加对象点、图像点（细化后）
if ret:
    obj_points.append(objp)

    corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    img_points.append(corners2)

    # 绘制和显示角
    cv.drawChessboardCorners(img, (9, 6), corners2, ret)
    cv.imshow('img', img)
    cv.waitKey(0)

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)


print("Camera matrix : \n")
print(mtx)
print("Distortion coefficients : \n")
print(dist)

cv.destroyAllWindows()
