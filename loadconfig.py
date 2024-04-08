import os
import sys
import logging

logging.basicConfig(format=(
    '%(asctime)s - %(levelname)s - '
    '[%(filename)s - %(funcName)s - Line %(lineno)d]: '
    '%(message)s'
), level=logging.INFO)

from src.tools.yaml_operations import fill_dict_from_yaml
from src.table_setup.table_setup import rect_names1, rect_names2, rect_names3, rect_names4, rect_names5, rect_names6, rect_names7, rect_names8, rect_names9, rect_names10, rect_names11, rect_names12, rect_names13, rect_names14, rect_names15, rect_names16, rect_names17, rect_names18, rect_names19, rect_names20, button_power


# config
filled_room_config = {}
filled_room_rects = {}
template_dir = None

# strategy
strategy_preflop = {}
strategy_postflop = {}


def load_config():
    
    # 读取默认房间配置（在config路径下）
    global filled_room_config
    room_dict = {
        'window_title': None,
        'platform': None,
        'max_players': None,
        'big_blind': None,
        'small_blind': None,
        'bet1_power': None,
        'bet2_power': None,
        'bet3_power': None,
        'bet4_power': None,
        'bet5_power': None,
    }
    script_dir = os.path.dirname(__file__)
    room_config_yaml = os.path.join(script_dir, 'config', 'room_config.yaml')
    filled_room_config = fill_dict_from_yaml(room_dict, room_config_yaml)
    
    # 根据房间配置，读取对应的rectangles配置（在config路径下）
    global filled_room_rects
    rects_dict = {}
    keylist = []
    for i in range(1, 21):
        keylist.extend(eval(f'rect_names{i}'))

    for key in keylist:
        rects_dict[key] = None

    room_rects_yaml = os.path.join(script_dir, 'config', f"{filled_room_config['platform']}{filled_room_config['max_players']}.yaml")
    filled_room_rects = fill_dict_from_yaml(rects_dict, room_rects_yaml)

    # 获取图片模板路径（用于图像匹配）
    global template_dir
    script_dir = os.path.dirname(__file__)
    template_dir = os.path.join(script_dir, 'config', 'templates', f"{filled_room_config['platform']}")
    # print(f"template_dir: {template_dir}")

    # 获取游戏策略配置



load_config()
# print(filled_room_config)
# print(filled_room_rects)