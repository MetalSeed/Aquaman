

# 输入table窗口的截图，用鼠标画框，来捕捉框的坐标，作为item的mapping数据
# 


# 配置：最大人数（8 或 9）

# 输入：文件编号，自动对应到识别类型（1-4，每个item要画3次框）：

# 识别1：   玩家信息：手牌状态，行动决定，行动数字，后手筹码，头像位置。 共5x9个
#          输   入：1-3.png （要求全员入池，行动数字有偿有短）

# 识别2：   牌桌信息：上轮底池，当前底池，5张公共牌位置，hero额外信息：fold， call, raise, rb1, rb2, rb3, rb4, eb5。 共15个
#          输   入：4-6.png （要求 river轮，4.png底池长，5.png底池短，6.png正常，可两人模拟）

# 识别3：   玩家信息：BTN范围。 共1x1个
#          输   入：7-max_players*3.png （从下家顺时针，每个button图标）

# 识别4：   玩家ID，buyin, seatdown, leave, joinroom, closepromotion
#          输   入：n

# 输出：文件编号.txt，保存矩形框的坐标
# 总结：用table_mapping读取并总结出mapping坐标，用于screen_craper_mapping.py

import os
import cv2
from aqm_utils import get_file_full_name

# wepoker 不同的矩形框名字列表
rect_names1 = ["P0_status", "P0_desicion", "P0_pot", "P0_funds", "P0_photo", "P1_status", "P1_desicion", "P1_pot", "P1_funds", "P1_photo", "P2_status", "P2_desicion", "P2_pot", "P2_funds", "P2_photo", "P3_status", "P3_desicion", "P3_pot", "P3_funds", "P3_photo", "P4_status", "P4_desicion", "P4_pot", "P4_funds", "P4_photo", "P5_status", "P5_desicion", "P5_pot", "P5_funds", "P5_photo", "P6_status", "P6_desicion", "P6_pot", "P6_funds", "P6_photo", "P7_status", "P7_desicion", "P7_pot", "P7_funds", "P7_photo", "P8_status", "P8_desicion", "P8_pot", "P8_funds", "P8_photo"]
rect_names2 = ["Pot", "Total_Pot", "Board1", "Board2", "Board3", "Board4", "Board5", "Hero_Fold", "Hero_Bet", "Hero_Call", "bet1", "bet2", "bet3", "bet4", "bet5"]
rect_names3 = ["Dealer"]
rect_names4 = ["Player_ID"]

# 全局变量
rectangles = []  # 存储矩形框的坐标
drawing = False  # 标记是否开始画图
current_rectangle = (-1, -1, -1, -1)  # 当前矩形的坐标

def draw_rectangle(event, x, y, flags, param):
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
    """
    计算文本的显示位置。
    :param index: 当前项目的索引。
    :param start_x: 第一列的起始X坐标。
    :param start_y: 文本起始Y坐标。
    :param column_width: 列宽。
    :param max_items_per_column: 每列的最大项目数。
    :param height: 图像高度，用于计算最大项目数。
    :return: (x, y) 文本的显示位置。
    """
    column_index = index // max_items_per_column
    x = start_x + column_index * column_width
    y = start_y + (index % max_items_per_column) * 30  # 假设每行文本高度约30像素
    return x, y

def save_rectangles_to_file(filename, rect_names, rectangles):
    """
    将矩形框名字和坐标保存到文件中。
    :param filename: 要保存的文件名。
    :param rect_names: 矩形框的名字列表。
    :param rectangles: 矩形框坐标列表。
    """
    with open(filename, 'w') as file:
        # 确保有相同数量的名字和矩形框
        assert len(rect_names) == len(rectangles), "矩形名字和坐标数量不匹配"
        
        # 写入每个矩形框的名字和坐标
        for name, rect in zip(rect_names, rectangles):
            file.write(f"{name}: {rect}\n")


def main(max_players, image_number):
    global rectangles

    image_name = f"{image_number}.png"  # 构造文件名

    # 根据图片编号选择对应的矩形框名字列表
    if 1 <= image_number <= 3:
        rect_names = rect_names1[:max_players*5]  # 根据玩家数调整列表长度
    elif 4 <= image_number <= 6:
        rect_names = rect_names2
    elif 7 <= image_number <= 7 + max_players * 3 - 1:
        rect_names = rect_names3
    else:
        rect_names = rect_names4


    image_path = get_file_full_name(image_name, 2, 'data', 'input', 'table_setup')
    img = cv2.imread(image_path)

    # 扩展图片以在右侧留白，用于显示文本
    height, width = img.shape[:2]
    extended_width = 900  # 根据需要调整
    extended_img = cv2.copyMakeBorder(img, 0, 0, 0, extended_width, cv2.BORDER_CONSTANT, value=(255, 255, 255))

    cv2.namedWindow('table_setup')
    cv2.setMouseCallback('table_setup', draw_rectangle)

    start_x = width + 10  # 从原图右侧开始显示文本
    start_y = 20  # 从顶部开始显示文本
    column_width = 200  # 每列的宽度
    max_items_per_column = height // 30  # 根据图像高度和文本高度计算每列最大项目数

    while True:
        img_copy = extended_img.copy()

        for idx, name in enumerate(rect_names):
            x, y = calculate_text_position(idx, start_x, start_y, column_width, max_items_per_column, height)
            cv2.putText(img_copy, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)


        # 绘制已经定义的矩形框
        for idx, rect in enumerate(rectangles):
            cv2.rectangle(img_copy, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
            # 在矩形框名称旁边显示坐标
            text_position = (width + 10, 30 * (idx+1))
            cv2.putText(img_copy, f"{rect_names[idx]}: {rect}", text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

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

    # 提示最大玩家数
    max_players = 8
    print(f"最大玩家数: {max_players}")

    # 提示用户输入图片编号
    image_number = int(input("请输入图片编号: "))
    
    main(max_players, image_number)

    # 选择对应的 rect_names 列表
    if 1 <= image_number <= 3:
        rect_names = rect_names1[:max_players * 5]  # 调整长度以匹配玩家数
    elif 4 <= image_number <= 6:
        rect_names = rect_names2
    elif 7 <= image_number <= 7 + max_players * 3 - 1:
        rect_names = rect_names3
    else:
        rect_names = rect_names4
    
    # 构造文件名和保存路径
    filename = f"{image_number}.txt"
    full_path = get_file_full_name(filename, 2, 'data', 'output', 'table_setup')
    
    # 调用函数保存数据到文件，确保传递正确的 rect_names 列表
    save_rectangles_to_file(full_path, rect_names, rectangles)

