import cv2
import numpy as np


def calculate_marker_orientation(corners):
    """
    计算 ArUco 标记的方向向量。

    :param corners: ArUco 标记的四个角点坐标
    :return: 方向向量 (dx, dy)
    """
    # 获取标记的中心点
    center_x = int(np.mean(corners[:, 0]))
    center_y = int(np.mean(corners[:, 1]))

    # 假设 ArUco 标记的第 0 号角点是最左边的角点
    dx = corners[0, 0] - center_x
    dy = corners[0, 1] - center_y

    return dx, dy


def calculate_rotation_angle(dx, dy):
    """
    计算方向向量相对于图像顶部的顺时针旋转角度。

    :param dx: 方向向量的 x 分量
    :param dy: 方向向量的 y 分量
    :return: 顺时针旋转角度（度）
    """
    # 使用 atan2 计算角度，返回值范围 [-pi, pi]
    angle_rad = np.arctan2(dy, dx)

    # 将弧度转换为角度
    angle_deg = np.degrees(angle_rad)

    # 因为OpenCV的坐标系y轴向下，我们计算的是从y轴开始的逆时针角度，
    # 所以我们需要调整角度使其符合顺时针测量的标准（从x轴开始）
    rotation_angle = (90 - angle_deg) % 360

    return rotation_angle


def main():
    # 加载图像
    image_path = 'image/test_image.png'
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not load image.")
        return

    # 转为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 初始化 ArUco 检测器
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
    parameters = cv2.aruco.DetectorParameters()
    # 检测 ArUco 标记
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, rejected_img_points = detector.detectMarkers(gray)

    if ids is not None:
        for i in range(len(ids)):
            # 获取当前标记的角点坐标
            current_corners = corners[i][0]

            # 计算标记的方向向量
            orientation_vector = calculate_marker_orientation(current_corners)

            # 计算旋转角度
            rotation_angle = calculate_rotation_angle(orientation_vector[0], orientation_vector[1])

            print(f"ArUco ID {ids[i]} 顺时针旋转角度: {rotation_angle:.2f} 度")

            # 显示结果图像
            cv2.imshow('ArUco Detection', image)
            cv2.waitKey(0)
    else:
        print("No ArUco markers detected.")

    cv2.destroyAllWindows()


if "__main__" != __name__:
    pass
else:
    main()
