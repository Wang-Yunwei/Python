import cv2

# try:
#     fourcc = cv2.VideoWriter_fourcc(*'XVID')
#     print("VideoWriter_fourcc is available.")
# except AttributeError:
#     print("VideoWriter_fourcc is not available in this version of OpenCV.")

# 创建窗口
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', 800, 600)
cv2.moveWindow('image', 700, 400)

# 获取视频设备/从文件中读取视频帧
cap = cv2.VideoCapture(0)

detector = cv2.QRCodeDetector()

while True:
    # 从摄像头读取视频帧
    ret, frame = cap.read()

    # 检测二维码
    # data, bbox, _ = detector.detectAndDecode(frame)

    # if bbox is not None:
    #     # 绘制二维码边界框
    #     n = len(bbox)
    #     for i in range(n):
    #         pt1 = tuple(map(int, bbox[i][0]))
    #         pt2 = tuple(map(int, bbox[(i + 1) % n][0]))
    #         cv2.line(frame, pt1, pt2, (0, 255, 0), 3)
    #
    #     if data:
    #         print("解码内容:", data)
    #         # 提取二维码中的坐标或指令（例如："x=1.2,y=3.4"）
    #         # 此处假设二维码内容为逗号分隔的坐标
    #         try:
    #             x, y = map(float, data.split(','))
    #             print("x:", x)
    #             print("y:", y)
    #         except:
    #             pass
    # else:
    #     print("二维码检测失败!")

    # 将视频帧在窗口展示
    cv2.imshow('image', frame)
    # 监听按键
    key = cv2.waitKey(40)
    if key & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
