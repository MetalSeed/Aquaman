import os
import sys
import cv2
from PIL import Image

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

def print_table_dict(table_info):
    for key, value in table_info.items():
        if key == 'players':
            for player in value:
                player_info = ', '.join(f"{player_key}: {player_value}" for player_key, player_value in player.items())
                print(player_info)
        else:
            print(f"{key}: {value}")

def main():
    table = Table()
    round = Round()
    hands = Hands()


    while True:
        # 提示用户输入图片编号
        image_number = input("请输入图片编号: ")
        if image_number.lower() == 'q':
            break
        # 构造文件名和读取路径
        image_name = f"{image_number}.png"  
        ws_input_path = get_file_full_name(image_name, 'data', 'test')

        # screen input
        windowshot_numpy = cv2.imread(ws_input_path)
        windowshot_pil = Image.fromarray(windowshot_numpy)
        table.prr.windowshot_input(windowshot_pil)

        # IR
        table.update_table_info()
        # table.update_players_data()
        table_dict = table.get_table_dict()
        print_table_dict(table_dict)

        # update hands
        round.tabledict2round(table_dict)
        hands.add_round(round)

        hands.print_hands_info()

        # make decision
        decision = input("请输入你的决策: ") # 'F', 'X', 'C', 'R1' - 'R5'   
        # dicision = get_decision(hands)
        hands.add_hero_decision(decision)
        
        

if __name__ == '__main__':
    main()


