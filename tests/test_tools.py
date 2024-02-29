# 使用示例

import os
import sys

# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(parent_dir)
from src.tools.aqm_utils import draw_multiple_rectangles_and_save, get_file_full_name


script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(grandparent_dir)

# draw_rectangles test
image_path = get_file_full_name('1.png', 'data', 'input', 'table_setup')
save_path  = get_file_full_name('1_new.png', 'data', 'output', 'table_setup')

table_region = (128, 259, 408, 556)
action_region = (100, 801, 183, 869)
rectangles = [table_region, action_region]  # 给定的多个矩形框参数

draw_multiple_rectangles_and_save(image_path, rectangles, save_path)