import cv2
import numpy as np


def order_points(pts):
    """将四个角点按顺时针顺序排列（左上、右上、右下、左下）"""
    # 按x坐标排序，得到左右两组点
    x_sorted = pts[np.argsort(pts[:, 0])]
    left = x_sorted[:2]  # 左侧两点
    right = x_sorted[2:]  # 右侧两点

    # 左侧两点按y坐标排序，得到左上（较小y）和左下
    left = left[np.argsort(left[:, 1])]
    (tl, bl) = left

    # 右侧两点按y坐标排序，得到右上和右下
    right = right[np.argsort(right[:, 1])]
    (tr, br) = right

    # 返回顺时针顺序的四个点：左上、右上、右下、左下
    return np.array([tl, tr, br, bl], "float32")


# 原始角点坐标（假设为检测到的ArUco标记角点）
corners = np.array([
    [129., 217.],
    [301., 74.],
    [452., 255.],
    [265., 402.]
], np.float32)

# 将角点按顺时针顺序排列
ordered_corners = order_points(corners)

# 创建空白图像（假设尺寸为480x640）
image = np.zeros((480, 640, 3), np.uint8)

# 绘制标注的角点顺序
for i, (x, y) in enumerate(ordered_corners):
    cv2.putText(
        image,
        str(i + 1),
        (int(x), int(y)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),  # 红色文本
        2
    )

# 绘制闭合的多边形连线（验证顺时针顺序）
pts = ordered_corners.astype(np.int32)
cv2.polylines(
    image,
    [pts],
    True,
    (0, 255, 0),  # 绿色线条
    2
)

# 显示图像
cv2.imshow("ArUco Corners (Ordered)", image)
cv2.waitKey(0)
cv2.destroyAllWindows()