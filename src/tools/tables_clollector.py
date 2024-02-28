# tableshots for table_setup or hands_converterß
import datetime
import time
import cv2
import numpy as np
from aqm_utils import get_file_full_name
from screen_operations import ScreenshotUtil

def compare_images_in_region(image1, image2, region=None, threshold=0.9):
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

    # 计算两个灰度图像的结构相似度指数
    score, _ = cv2.compareHist(img1_gray, img2_gray, cv2.HISTCMP_CORREL)
    # 比较相似度阈值
    return score < threshold

def main(window_title, template, action_region, table_region):
    last_screenshot = None
    screenshot_util = ScreenshotUtil(window_title)
    
    while True:
        windowshot = screenshot_util.capture_screen()
        if windowshot is None:
            print("Failed to capture screenshot.")
            time.sleep(1)
            continue
        if screenshot_util.match_template_in_screenshot(windowshot, template, action_region):
            print("Template found in screenshot.")

            if last_screenshot and not compare_images_in_region(last_screenshot, windowshot, table_region):
                print("Screenshots are similar; not saving.")
            else:
                now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                save_path = get_file_full_name(f"{now}.png", 2, 'data', 'output', 'table_setup')
                screenshot_util.save_screenshot(windowshot, save_path)
                print(f"Screenshot saved: {save_path}")
                last_screenshot = windowshot
        else:
            print("Template not found in screenshot.")
        time.sleep(1)

if __name__ == "__main__":
    window_title = "雷电模拟器-1"
    table_region = (128, 259, 408, 556)
    action_region = (100, 801, 183, 869)
    icon_fold_path = get_file_full_name('fold.jpg', 2, 'data', 'input', 'talbes_collector')
    template = cv2.imread(icon_fold_path)
    
    main(window_title, template, action_region, table_region)