import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image

###############################
#       添加项目根目录          #        
###############################
import os
import sys
# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(grandparent_dir)

from src.tools.aqm_utils import get_file_full_name
from src.recognizer.image_recognizer import ImageRecognizer
IRtool = ImageRecognizer()

# 初始化全局变量
rects = []  # 用于存储用户绘制的所有矩形
current_rect = []  # 用于存储当前正在绘制的矩形的起始点和终点
global img  # 使img为全局变量以便在函数间共享
global windowshot


def mouse_callback(event, x, y, flags, param):
    global current_rect, rects, img
    if event == cv2.EVENT_LBUTTONDOWN:
        current_rect = [(x, y)]  # 开始绘制矩形框，记录起始点
    elif event == cv2.EVENT_MOUSEMOVE and current_rect:
        # 按下鼠标左键并移动时，实时更新并显示矩形框
        img_copy = img.copy()
        cv2.rectangle(img_copy, current_rect[0], (x, y), (0, 0, 255), 2)  # 使用红色绘制矩形框
        cv2.imshow("Image", img_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        # 完成矩形框绘制，记录终点，保存矩形框
        current_rect.append((x, y))
        rects.append(tuple(current_rect))
        current_rect = []  # 重置当前矩形
        process_rect(img, rects[-1])  # 处理并输出最新矩形区域的颜色信息

def draw_rects(img, rects):
    for rect in rects:
        cv2.rectangle(img, rect[0], rect[1], (0, 255, 0), 2)  # 绘制矩形


def find_dominant_colors_and_ranges_in_hsv(cropped_img, k=3):
    # 转换到HSV颜色空间，进行K-means聚类，等等
    hsv_img = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_BGR2HSV)
    
    # 将图像数据转换为二维数组，每行一个像素，每列一个颜色通道
    pixels = hsv_img.reshape((-1, 3))
    
    # 使用K-means聚类算法找到最主要的k个颜色
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # 获取每个聚类中心（主要颜色）在HSV空间的值
    dominant_colors_hsv = np.uint8(kmeans.cluster_centers_)
    
    # 初始化颜色范围列表
    color_ranges = []

    for i in range(k):
        cluster_pixels = pixels[kmeans.labels_ == i]
        min_vals = np.min(cluster_pixels, axis=0)
        max_vals = np.max(cluster_pixels, axis=0)
        color_ranges.append((min_vals, max_vals))
    
    # 计算每个聚类的大小，估计颜色占比
    _, counts = np.unique(kmeans.labels_, return_counts=True)
    total_count = np.sum(counts)
    
    # 计算每种颜色的占比
    color_ratios = counts / total_count
    sorted_indices = np.argsort(-color_ratios)
    sorted_colors_hsv = dominant_colors_hsv[sorted_indices]
    sorted_ratios = color_ratios[sorted_indices]
    sorted_color_ranges = [color_ranges[i] for i in sorted_indices]

    # 返回排序后的颜色、占比和颜色范围
    return sorted_colors_hsv, sorted_ratios, sorted_color_ranges

def process_image(file_path):
    global img, windowshot
    windowshot = Image.open(file_path)
    img = cv2.imread(file_path)
    if img is None:
        print("Failed to load the image.")
        return

    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", mouse_callback)

    while True:
        img_copy = img.copy()
        draw_rects(img_copy, rects)  # 绘制所有已完成的矩形
        cv2.imshow("Image", img_copy)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # 按q退出
            break
        elif key == ord('c') and rects:  # 按c取消最后一个框
            rects.pop()

    cv2.destroyAllWindows()

def test_color_ratio(croped_img, rect, color_range):
    image_array = np.array(croped_img)
    hsv_img = cv2.cvtColor(image_array, cv2.COLOR_BGR2HSV)
    
    # 初始化颜色匹配像素计数
    match_count = 0
    total_pixels = hsv_img.shape[0] * hsv_img.shape[1]
    
    for key, (lower, upper) in color_range.items():
        # 将颜色范围的下限和上限转换为NumPy数组
        lower_bound = np.array(lower, dtype="uint8")
        upper_bound = np.array(upper, dtype="uint8")
        
        # 根据颜色范围创建掩码
        mask = cv2.inRange(hsv_img, lower_bound, upper_bound)
        
        # 使用掩码计算匹配的像素数量
        match_count += cv2.countNonZero(mask)
    
    # 计算匹配颜色的像素占比
    color_ratio = match_count / total_pixels
    print(f"Matching color ratio: {color_ratio:.2f}")

    return color_ratio


def process_rect(img, rect):
    # 输出矩形的坐标，按照指定的格式
    print(f"current_rectangle = ({rect[0][0]}, {rect[0][1]}, {rect[1][0]}, {rect[1][1]})")

    global target_color, windowshot
    # 从全局图像中裁剪出矩形区域
    cropped_img = windowshot.crop((rect[0][0], rect[0][1], rect[1][0], rect[1][1]))
    # 输出OCR识别结果
    words = IRtool.recognize_string(cropped_img)
    txt = IRtool.recognize_black_digits(cropped_img)
    print(f"OCR Result: {txt}")
    # 输出目标颜色占比
    test_color_ratio(cropped_img, rect, target_color)

    # 获取颜色信息
    dominant_colors_hsv, sorted_ratios, sorted_color_ranges = find_dominant_colors_and_ranges_in_hsv(cropped_img)

    # 输出颜色信息
    for color_hsv, ratio, color_range in zip(dominant_colors_hsv, sorted_ratios, sorted_color_ranges):
        print(f"Color (HSV): {color_hsv}, Ratio: {ratio:.2f}, Range: {color_range}")


red1 = {
        'red1': ([122, 126, 222], [125, 211, 239]), 
    }
red2 = {
        'red2': ([122, 95, 132], [126, 211, 148]), 
    }
blue = {
        'blue': ([ 13, 168, 214], [ 17, 227, 239]),  # bet call
    }

orangeraise = {
        'orange': ([105, 127,  66], [110, 237, 239]), 
    }
greencheck = {
        'green': ([ 37, 146,  56], [ 43, 245, 207]), 
    }

poker_back = {
        'poker': ([117,  67, 198], [126, 135, 222]), 
    }
void_black1 = {
        'black': ([150,   3,  33], [150,  39, 107]), 
    }
color_ranges_pocker = {
    'c': ([36, 25, 25], [86, 255,255]),  # 绿色 club
    'h': ([170, 100, 50], [180, 255, 255]),  # 红色 heart
    's': ([0, 0, 0], [180, 255, 30]),     # 黑色 spade
    'd': ([94, 80, 2], [126, 255, 255]),  # 蓝色 diamond
}
club = {
    'c': ([36, 25, 25], [86, 255,255]),  # 绿色 club
}
heart = {
    'h': ([170, 100, 50], [180, 255, 255]),  # 红色 heart
}
spade = {
    's': ([0, 0, 0], [180, 255, 30]),     # 黑色 spade
}
diamond = {
    'd': ([94, 80, 2], [126, 255, 255]),  # 蓝色 diamond
}
target_color = heart

if __name__ == "__main__":
    # file_name = input("请输入文件名: ")
    file_name = '211'
    
    img_path = f"{file_name}.png"
    file_path = get_file_full_name(img_path, 'data', 'test')
    process_image(file_path)