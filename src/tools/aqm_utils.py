# 通用函数工具

import os
import time
import cv2
import pyautogui



def get_file_full_name(file_name, up_levels, *subfolders):
    # 获取当前脚本的绝对路径
    script_dir = os.path.dirname(__file__)
    
    # 根据指定的层数向上遍历获取父目录
    for _ in range(up_levels):
        script_dir = os.path.dirname(script_dir)
    
    # 最终的父目录即为向上遍历后的结果
    final_dir = script_dir

    # 构建目标文件的绝对路径，包括可变数量的子文件夹路径
    file_full_name = os.path.join(final_dir, *subfolders, file_name)
    return file_full_name
#示例
# file_full_name = get_file_full_name('1.jpg', 2, 'data', 'output', 'table_setup')

# 画框工具
def draw_multiple_rectangles_and_save(image_path, rectangles, save_path):
    # 读取图片
    img = cv2.imread(image_path)
    
    # 遍历矩形框列表，画每个矩形框
    # 每个rectangle参数是(x, y, width, height)，其中(x, y)是矩形框左上角的坐标
    for rectangle in rectangles:
        x1, y1, x2, y2 = rectangle
        # 画矩形框，参数依次为图片、左上角坐标、右下角坐标、颜色(BGR格式)、线条粗细
        # 使用红色(0, 0, 255)作为矩形框的颜色
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    
    # 保存图片
    cv2.imwrite(save_path, img)
    print(f"保存修改后的图片到 {save_path}")

# 使用示例
image_path = get_file_full_name('1.png', 2, 'data', 'output', 'tables_collector')
save_path  = get_file_full_name('1_new.png', 2, 'data', 'output', 'tables_collector')

table_region = (128, 259, 408, 556)
action_region = (100, 801, 183, 869)
rectangles = [table_region, action_region]  # 给定的多个矩形框参数

draw_multiple_rectangles_and_save(image_path, rectangles, save_path)
