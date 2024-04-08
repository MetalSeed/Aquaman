import os
import sys
import cv2
from PIL import Image

import logging
# 配置日志格式，包括时间、日志级别、文件名、所处函数名、所在行数和消息
# 使用括号将格式字符串分成多行，以提高可读性
logging.basicConfig(format=(
    '%(asctime)s - %(levelname)s - '
    '[%(filename)s - %(funcName)s - Line %(lineno)d]: '
    '%(message)s'
), level=logging.INFO)

# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(grandparent_dir)

from loadconfig import load_config
from src.recognizer.nlth_table import Table
from src.tools.aqm_utils import get_file_full_name
from src.hands_converter.class_hands import Round, Hands


def hands_input(hands, table, windowshotid, decision):
    # 提示用户输入图片编号
    image_name = windowshotid
    # 构造文件名和读取路径
    image_name = f"{image_name}.png"  
    ws_input_path = get_file_full_name(image_name, 'data', 'test')
    print(f"当前处理的图片是: {ws_input_path}")

    # screen input
    windowshot_pil = Image.open(ws_input_path)
    table.prr.windowshot_input(windowshot_pil)

    # IR
    table.recognize_info()
    table.print_table_dict()
    table_dict = table.get_table_dict()
    
    # update hands
    round = Round()
    round.tabledict2round(table_dict)
    hands.add_round(round)

    hands.print_hands_info()

    print(f"你的决策是: {decision}")
    hands.add_hero_action(decision)

def hands_input_loop():
    while True:
        # 提示用户输入图片编号
        image_number = input("请输入图片编号: ")
        if image_number.lower() == 'q':
            break
        # make decision
        # dicision = get_decision(hands)
        decision = input("请输入你的决策: ") # 'F', 'X', 'C', 'R1' - 'R5'   
        hands_input(image_number, decision)

# 测试的table shots和对应决策
input_dict1 = {
    'w11': 'R1',
    'w12': 'X',
    'w13': 'X',
    'w14': 'X',
}
input_dict2 = {
    'w21': 'C',
    'w22': 'C',
    'w23': 'X',
    'w24': 'X',
    'w25': 'F',
}
input_dict3 = {
    'w31': 'C',
    'w32': 'X',
    'w33': 'C',
    'w34': 'X',
    'w35': 'R1',
    'w36': 'C',
}
input_dict4 = {
    'w41': 'X',
    'w42': 'X',
    'w43': 'X',
    'w44': 'X',
}

def main():
    hands = Hands()
    table = Table()

    decision_dict = input_dict3
    for image_name, decision in decision_dict.items():
        hands_input(hands, table, image_name, decision)

    # hands_input_loop()

if __name__ == '__main__':
    main()

# 检查座位是空的情况下， 起始坐标的问题，从join_hands里跳1或者2个位置

# 要看怎么释放round的存储空间, hands = None,然后重新赋值就行了