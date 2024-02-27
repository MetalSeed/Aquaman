# tableshots for table_setup or hands_converter


import cv2
import numpy as np

from recognizer.image_reconizer_matching import find_template_in_region

def compare_image_regions(image1, image2, region):
    # 裁剪指定区域
    x, y, width, height = region
    cropped_img1 = image1[y:y+height, x:x+width]
    cropped_img2 = image2[y:y+height, x:x+width]

    # 比较两个区域
    difference = cv2.subtract(cropped_img1, cropped_img2)
    b, g, r = cv2.split(difference)

    if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
        print("两个区域相同。")
        return True
    else:
        print("两个区域不相同。")
        return False


# 使用示例
image_path1 = 'path/to/your/first/image.jpg'
image_path2 = 'path/to/your/second/image.jpg'
# 读取图片
img1 = cv2.imread(image_path1)
img2 = cv2.imread(image_path2)

region = (100, 100, 50, 50)  # 示例区域

compare_image_regions(img1, img2, region)

# 每秒截图
# 比较Fold
# 去重