import cv2
import numpy as np


def calculate_distances_to_edges(image, corners):
    """
    计算 ArUco 标记的中心点到图像四个边缘的距离。

    :param image: 输入图像
    :param corners: ArUco 标记的角点坐标
    :return: 到上、右、下、左边缘的距离
    """
    # 计算 ArUco 标记的中心点
    center_x = int(np.mean(corners[:, 0]))
    center_y = int(np.mean(corners[:, 1]))

    # 获取图像尺寸
    height, width = image.shape[:2]

    # 计算到四个边缘的距离
    distance_top = center_y
    distance_right = width - center_x
    distance_bottom = height - center_y
    distance_left = center_x

    return distance_top, distance_right, distance_bottom, distance_left


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
    """
    1.从视频设备中获取视频流\n
    2.识别视频流中的ArUco图像位置信息以及角点角度
    """
    # 初始化 ArUco 检测器
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    # 创建窗口
    cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
    # cv2.resizeWindow('image', 800, 600)
    # cv2.moveWindow('image', 700, 400)

    # 获取视频设备/从文件中读取视频帧
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        # 转为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 检测 ArUco 标记
        corners, ids, rejected_img_points = detector.detectMarkers(gray)

        if ids is not None:
            print(f"ids_len{len(ids)}")
            # 遍历每个检测到的 ArUco 标记
            for i in range(len(ids)):
                # 绘制检测到的标记
                cv2.aruco.drawDetectedMarkers(frame, corners)

                # 获取当前标记的角点坐标
                current_corners = corners[i][0]
                # 计算标记的方向向量
                orientation_vector = calculate_marker_orientation(current_corners)

                # 计算旋转角度
                rotation_angle = calculate_rotation_angle(orientation_vector[0], orientation_vector[1])
                print(f"ArUco ID {ids[i]} 顺时针旋转角度: {rotation_angle:.2f} 度")

                # 计算到四个边缘的距离
                distances = calculate_distances_to_edges(frame, current_corners)

                print(f"ArUco ID {ids[i]} distances to edges (top, right, bottom, left): {distances}")

                # 在图像上显示距离信息
                center_x = int(np.mean(current_corners[:, 0]))
                center_y = int(np.mean(current_corners[:, 1]))
                cv2.putText(frame, f'Dist: {distances}', (center_x - 50, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 2)
                # 显示结果图像
                cv2.imshow('image', frame)
                # 监听按键
                key = cv2.waitKey(40)
                if key & 0xFF == ord('q'):
                    break
        else:
            print("No ArUco markers detected.")
            # 显示结果图像
            cv2.imshow('image', frame)
            # 监听按键
            key = cv2.waitKey(40)
            if key & 0xFF == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()


if __name__ != "__main__":
    pass
else:
    main()
