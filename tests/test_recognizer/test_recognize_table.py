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


def main(ws_input_path):
    table = Table()
    
    windowshot_pil = Image.open(ws_input_path)
    table.prr.windowshot_input(windowshot_pil)

    # 更新数据
    table.update_table_info()
    # table.update_players_data()


    table_info = table.get_table_dict()
    
    for key, value in table_info.items():
        if key == 'players':
            for player in value:
                player_info = ', '.join(f"{player_key}: {player_value}" for player_key, player_value in player.items())
                print(player_info)
        else:
            print(f"{key}: {value}")

if __name__ == '__main__':
    ws_input_path = get_file_full_name('w25.png', 'data', 'test')
    main(ws_input_path)

# status to be done