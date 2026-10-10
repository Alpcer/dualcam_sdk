import os
import cv2
import rgbsdk

sdk = rgbsdk.RgbSDK()

# 全部用默认参数启动（cam_path="/dev/video0", undistort=False, ...）
sdk.start()

# 或者显式指定：
# sdk.start("/dev/video0", True, 0.0, 0.0, 600, 400, 414.18)

# 在当前路径下创建输出文件夹
out_dir = os.path.join(os.getcwd(), "demo_output")
os.makedirs(out_dir, exist_ok=True)

count = 10
while count > 0 and sdk.grab():

    left  = sdk.retrieve_image(rgbsdk.IMAGE_FISHEYE_LEFT)
    right = sdk.retrieve_image(rgbsdk.IMAGE_FISHEYE_RIGHT)

    # left/right 已经是 numpy uint8（BGR 或灰度），可直接用 cv2.imwrite
    cv2.imwrite(os.path.join(out_dir, f"left_{count}.jpg"),  left)
    cv2.imwrite(os.path.join(out_dir, f"right_{count}.jpg"), right)

    count -= 1

sdk.stop()
print(f"图像已保存到: {out_dir}")