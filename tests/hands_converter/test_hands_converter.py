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


def main():
    hands = Hands()
    table = Table()

    while True:
        # 提示用户输入图片编号
        image_number = input("请输入图片编号: ")
        if image_number.lower() == 'q':
            break
        # 构造文件名和读取路径
        image_name = f"{image_number}.png"  
        ws_input_path = get_file_full_name(image_name, 'data', 'test')

        # screen input
        windowshot_pil = Image.open(ws_input_path)
        table.prr.windowshot_input(windowshot_pil)

        # IR
        table.clear()
        table.update_table_info()
        table.print_table_dict()
        table_dict = table.get_table_dict()
        
        # update hands
        round = Round()
        round.tabledict2round(table_dict)
        hands.add_round(round)

        hands.print_hands_info()

        # make decision
        decision = input("请输入你的决策: ") # 'F', 'X', 'C', 'R1' - 'R5'   
        # dicision = get_decision(hands)
        hands.add_hero_action(decision)
        
        

if __name__ == '__main__':
    main()

# 检查hero 在BTN BB SS的情况。人数少于5的情况。UTG，CO的情况

# 要看怎么释放round的存储空间