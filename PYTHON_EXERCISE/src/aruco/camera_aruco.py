import numpy as np
import cv2 as cv
import glob

# 终止标准
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# 定义 ArUco 字典和参数
aruco_dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_250)
board = cv.aruco.CharucoBoard_create(7, 5, 1, .8, aruco_dict)  # 7x5 的 Charuco 板
parameters = cv.aruco.DetectorParameters_create()

# 数组来存储所有图像中的对象点和图像点
obj_points = []  # 真实世界空间中的 3D 点
img_points = []  # 图像平面中的二维点

images = glob.glob('*.png')

# for fname in images:
img = cv.imread("../../image/66.png")
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# 检测 ArUco 标记
corners, ids, rejected = cv.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

if len(corners) > 0:  # 如果找到了 ArUco 标记
    # 提取更多角点
    _, corners_charuco, ids_charuco = cv.aruco.interpolateCornersCharuco(corners, ids, gray, board)

    if ids_charuco is not None and corners_charuco is not None and len(ids_charuco) > 4:  # 如果找到足够的角点
        obj_points.append(board.objPoints()[ids_charuco])
        img_points.append(corners_charuco)

        # 绘制 ArUco 标记和 Charuco 角点
        img_with_aruco = cv.aruco.drawDetectedMarkers(img.copy(), corners, ids)
        img_with_charuco = cv.aruco.drawDetectedCornersCharuco(img_with_aruco, corners_charuco, ids_charuco)
        cv.imshow('img', img_with_charuco)
        cv.waitKey(0)

# 执行相机校准
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)

print("Camera matrix : \n")
print(mtx)
print("Distortion coefficients : \n")
print(dist)

cv.destroyAllWindows()
