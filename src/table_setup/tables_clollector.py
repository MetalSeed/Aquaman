# tableshots for table_setup or hands_converterß
import datetime
import os
import sys
import time
import cv2
import numpy as np

# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(grandparent_dir)


from src.tools.aqm_utils import get_file_full_name

from src.tools.screen_operations import ScreenshotUtil

def same_images_in_region(image1, image2, region=None, threshold=1):
    # 比较两张图像指定区域的相似度。
    if image1 is None or image2 is None:
        print("图片不存在。")
        return False
    
    if region:
        image1 = image1.crop(region)
        image2 = image2.crop(region)
    
    img1 = np.array(image1)
    img2 = np.array(image2)

    # 转换为灰度图像进行比较
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # 计算两个图像的直方图
    hist1 = cv2.calcHist([img1_gray], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([img2_gray], [0], None, [256], [0, 256])
    
    # 将直方图的数据类型转换为 CV_32F 来满足 compareHist 的要求
    hist1 = hist1.astype(np.float32)
    hist2 = hist2.astype(np.float32)
    
    # 比较直方图
    score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return score >= threshold

def main(window_title, template, action_region, table_region):
    last_screenshot = None
    screenshot_util = ScreenshotUtil(window_title)
    
    while True:
        windowshot = screenshot_util.capture_screen()
        if windowshot is None:
            print("Failed to capture screenshot.")
            time.sleep(1)
            continue
        if screenshot_util.match_template_in_screenshot(windowshot, template, action_region, 0.9):
            print("Template found in screenshot.")

            if last_screenshot and same_images_in_region(last_screenshot, windowshot, table_region):
                print("Screenshots are similar; not saving.")
            else:
                now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                save_path = get_file_full_name(f"{now}.png", 'data', 'output', 'tables_collector')
                screenshot_util.save_screenshot(windowshot, save_path)
                print(f"Screenshot saved: {save_path}")
                last_screenshot = windowshot
        else:
            print("Template not found in screenshot.")
        time.sleep(1)

if __name__ == "__main__":
    window_title = "雷电模拟器-1"
    action_region = (100, 801, 183, 869)
    table_region = (128, 259, 408, 556)

    icon_fold_path = get_file_full_name('fold.png', 'data', 'input', 'tables_collector')
    template = cv2.imread(icon_fold_path)
    
    main(window_title, template, action_region, table_region)