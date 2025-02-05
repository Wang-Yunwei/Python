import numpy as np
import cv2 as cv
import glob

# 定义使用的ArUco字典
aruco_dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_50)
parameters = cv.aruco.DetectorParameters()

# 指定要使用的标记ID (23)
target_id = 23

# 加载所有标定图像路径
files = glob.glob('image/*.JPG')

obj_points = []  # 三维点在现实世界的空间
img_points = []  # 图像平面上的2d点

markerLength = 0.1  # Marker边长，单位为米

for file in files:
    # 读取图片
    img = cv.imread(file)
    # 转为灰度图
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # 检测所有ArUco标记
    detector = cv.aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None and target_id in ids:
        # 获取目标ID的索引
        index = np.where(ids == target_id)[0][0]

        # 将检测到的角点转换为对象点（假设标记放置在世界坐标系中的z=0平面上）
        objp = np.array([[0, 0, 0], [markerLength, 0, 0],
                         [markerLength, markerLength, 0], [0, markerLength, 0]], dtype=np.float32)

        # 添加对象点和图像点到各自的列表中，注意这里直接添加而不是再嵌套一层列表
        obj_points.append(objp)  # 现在是N x 3的数组
        img_points.append(corners[index].reshape(-1, 2).astype(np.float32))  # 现在是N x 2的数组

        # 绘制并显示检测到的标记
        cv.aruco.drawDetectedMarkers(img, corners, ids)
        cv.imshow('img', img)
        cv.waitKey(0)

cv.destroyAllWindows()

if len(obj_points) > 0:
    # 执行相机标定
    ret, cameraMatrix, distCoeffs, rvecs, tvecs = cv.calibrateCamera(
        objectPoints=obj_points,
        imagePoints=img_points,
        imageSize=gray.shape[::-1],
        cameraMatrix=None,
        distCoeffs=None
    )

    print("Camera matrix : \n")
    print(cameraMatrix)
    print("Distortion coefficients : \n")
    print(distCoeffs)

    # 保存结果到文件中
    np.savez('calibration_data.npz', camera_matrix=cameraMatrix, dist_coeffs=distCoeffs)
else:
    print("No valid data for calibration.")