# 导入 OpenCV 库
import cv2

# 1. 读取图像,替换为实际的图像路径,这里是当前目录下的 "bird.jpg"
image = cv2.imread("../../image/bird.jpg")

# 检查图像是否成功读取
if image is None:
    print("错误：无法加载图像，请检查路径是否正确。")
    exit()

# 图像基本操作
# 获取像素值 (RGB 格式)
# pixel_value = image[20, 20]  # 获取 (20, 20) 处的像素值
# print(f"[20,20]处的像数值为: {pixel_value}")

# 修改像素值
# image[20, 20] = [255, 255, 255]  # 将 (100, 100) 处的像素设置为白色

# 获取 ROI
# roi = image[50:150, 50:150]  # 获取 (50,50) 到 (150,150) 的区域

# 修改 ROI
# image[50:150, 50:150] = [0, 255, 0]  # 将 ROI 区域设置为绿色

# 从 RGB 转换为灰度图
# gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 高斯模糊
# blurred_img = cv2.GaussianBlur(image, (5, 5), 0)
# cv2.imshow("Display Image", blurred_img)

# Canny 边缘检测
# edges = cv2.Canny(image, 100, 200)
# print(edges)

# 腐蚀（Erosion）：将图像中的白色区域收缩
# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
# eroded_img = cv2.erode(image, kernel, iterations=1)
# cv2.imshow("Display Image", eroded_img)

# 膨胀（Dilation）：将图像中的白色区域扩展
# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
# dilated_img = cv2.dilate(image, kernel, iterations=1)
# cv2.imshow("Display Image", dilated_img)

# 检测轮廓
gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, threshold_img = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(threshold_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 绘制轮廓
# cv2.drawContours(image, contours, -1, (0, 255, 0), 3)

# 2. 显示图像,创建一个名为 "Display Image" 的窗口并在其中显示图像
# cv2.imshow("Display Image", image)

# 3. 等待用户按键,参数 0 表示无限等待直到用户按下任意键
key = cv2.waitKey(0)

# 4. 根据用户按键执行操作
if key == ord('s'):  # 如果按下 's' 键
    # 保存图像
    output_path = "saved_image.jpg"
    cv2.imwrite(output_path, image)
    print(f"图像已保存为 {output_path}")
else:  # 如果按下其他键
    print("图像未保存!")

# 5. 关闭所有窗口
cv2.destroyAllWindows()