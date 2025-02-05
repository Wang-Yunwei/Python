import cv2
import cv2.aruco as aruco
import numpy as np

# 假设你已经有了相机矩阵camera_matrix和畸变系数dist_coeffs
camera_matrix = np.array([[1.23279785e+03, 0.00000000e+00, 1.88362018e+03],
                          [0.00000000e+00, 1.23098254e+03, 1.37294703e+03],
                          [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist_coeffs = np.array([[-0.01481283,  0.00342299, -0.00211552, -0.00103415, -0.00040872]])

# ArUco字典和参数
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
parameters = aruco.DetectorParameters()

# 创建检测器对象
detector = aruco.ArucoDetector(aruco_dict, parameters)

# 加载图像或视频帧
frame = cv2.imread('image/DJI_20250110143131_0008_Z.JPG')  # 这里应该是你的图像加载逻辑

if frame is None:
    print("Error: Could not load image.")
else:
    # 转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 检测ArUco标记
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None:
        # 设置标记的实际边长，单位为米
        markerLength = 0.1  # 100 mm = 0.1 meters

        # 估计姿态
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, markerLength, camera_matrix, dist_coeffs)

        for i in range(len(ids)):
            # 绘制轴线辅助查看姿态
            cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], markerLength)

            # 计算并显示距离（以米为单位）
            distance = np.linalg.norm(tvecs[i])
            print(f"Marker ID {ids[i][0]} is {distance:.4f} meters away.")

        # 显示检测结果
        aruco.drawDetectedMarkers(frame, corners, ids)
        cv2.imshow('Detected Markers', frame)
        cv2.waitKey(0)  # 等待按键事件
        cv2.destroyAllWindows()