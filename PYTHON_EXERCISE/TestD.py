import cv2
import numpy as np

# 假设 corners 是检测到的角点坐标
corners = np.array([[[129., 217.]],
                   [[301.,  74.]],
                   [[452., 255.]],
                   [[265., 402.]]], np.float32)

# 在图像上绘制角点顺序
image = np.zeros((480, 640, 3), np.uint8)  # 假设空白图像
for i, (x, y) in enumerate(corners):
    cv2.putText(image, str(i+1), (int(x), int(y)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

# 绘制连线（验证是否顺时针）
pts = corners.reshape(-1, 2).astype(int)
cv2.polylines(image, [pts], True, (0, 255, 0), 2)

cv2.imshow("ArUco Corners", image)
cv2.waitKey(0)