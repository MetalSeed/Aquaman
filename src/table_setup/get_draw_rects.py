import os
import sys
import cv2
# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(grandparent_dir)

from src.tools.aqm_utils import get_file_full_name

rect_names = [
    "rect1", "rect2", 'rect3', 'rect4', 'rect5', 'rect6', 'rect7', 'rect8', 'rect9', 'rect10'
    ]

# 全局变量
rectangles = []  # 存储矩形框的坐标
drawing = False  # 标记是否开始画图
current_rectangle = (-1, -1, -1, -1)  # 当前矩形的坐标

def draw_rectangle(event, x, y):
    global rectangles, drawing, current_rectangle

    # 鼠标左键按下开始绘制
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        current_rectangle = (x, y, x, y)
    
    # 鼠标移动更新矩形的宽和高
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            current_rectangle = (current_rectangle[0], current_rectangle[1], x, y)
    
    # 鼠标左键释放结束绘制
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rectangles.append(current_rectangle)
        current_rectangle = (-1, -1, -1, -1)

def calculate_text_position(index, start_x, start_y, column_width, max_items_per_column, height):
    column_index = index // max_items_per_column
    x = start_x + column_index * column_width
    y = start_y + (index % max_items_per_column) * 30  # 假设每行文本高度约30像素
    return x, y

def save_rectangles_to_file(filename, rect_names, rectangles):
    with open(filename, 'w') as file:
        # 确保有相同数量的名字和矩形框
        assert len(rect_names) == len(rectangles), "矩形名字和坐标数量不匹配"
        
        # 写入每个矩形框的名字和坐标
        for name, rect in zip(rect_names, rectangles):
            file.write(f"{name}: {rect}\n")


def main(image_path):
    global rectangles
    img = cv2.imread(image_path)

    # 如果文件不存在，退出
    if img is None:
        print(f"无法读取图像 {image_path}。")
        return

    # 扩展图片以在右侧留白，用于显示文本
    height, width = img.shape[:2]
    extended_width = 900  # 根据需要调整
    extended_img = cv2.copyMakeBorder(img, 0, 0, 0, extended_width, cv2.BORDER_CONSTANT, value=(255, 255, 255))

    cv2.namedWindow('get_draw_rects')
    cv2.setMouseCallback('get_draw_rects', draw_rectangle)

    start_x = width + 10  # 从原图右侧开始显示文本
    start_y = 20  # 从顶部开始显示文本
    column_width = 200  # 每列的宽度
    max_items_per_column = height // 30  # 根据图像高度和文本高度计算每列最大项目数

    while True:
        img_copy = extended_img.copy()

        # 右侧输出所有矩形名称
        for idx, name in enumerate(rect_names):
            x, y = calculate_text_position(idx, start_x, start_y, column_width, max_items_per_column, height)
            cv2.putText(img_copy, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # 绘制已经定义的矩形框
        for idx, rect in enumerate(rectangles):
            cv2.rectangle(img_copy, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
            # 在矩形框名称旁边显示坐标
            x, y = calculate_text_position(idx, start_x, start_y, column_width, max_items_per_column, height)
            text_position = (x + 150, y)
            cv2.putText(img_copy, f"done", text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            # cv2.putText(img_copy, f"{rect_names[idx]}: {rect}", text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        if current_rectangle != (-1, -1, -1, -1):
            cv2.rectangle(img_copy, (current_rectangle[0], current_rectangle[1]), (current_rectangle[2], current_rectangle[3]), (0, 0, 255), 2)
        cv2.imshow('table_setup', img_copy)

        # 检查按键事件
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or len(rectangles) >= len(rect_names):
            break
        elif key == ord('c') and rectangles:
            # 按 'c' 删除最后一个矩形框
            rectangles.pop()
    
    cv2.destroyAllWindows()
    for idx, rect in enumerate(rectangles):
        print(f"{rect_names[idx]}: {rect}")


if __name__ == '__main__':
    # 提示用户输入图片编号
    image_number = int(input("请输入图片编号: "))
    
    # 构造文件名和读取路径
    image_name = f"{image_number}.png"  
    image_path = get_file_full_name(image_name, 'data', 'test')
    main(image_path)

    # 构造文件名和保存路径
    save_path = get_file_full_name(f"{image_number}.txt", 'data', 'test')
    save_rectangles_to_file(save_path, rect_names, rectangles)
