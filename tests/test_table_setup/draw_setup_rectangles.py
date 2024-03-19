# 从yaml里渎，画
import os
import sys

# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
parent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(parent_dir)


from src.tools.aqm_utils import draw_multiple_rectangles_and_save, get_file_full_name
from src.tools.yaml_operations import read_tuple_from_yaml
from src.table_setup.table_setup import rect_names1, rect_names2, rect_names3, rect_names4, rect_names5, rect_names6, rect_names7, rect_names8, rect_names9, rect_names10, rect_names11, rect_names12, rect_names13, rect_names14, rect_names15, rect_names16, rect_names17, rect_names18, rect_names19, rect_names20

# 全局变量
rectangles = []  # 存储矩形框的坐标

def main(image_path, save_path, yaml_path):
    global rectangles
    # 加载keys
    key_list = []
    for i in range(1, 21):
        key_list.extend(eval(f'rect_names{i}'))

    # 读取 rectangles
    for key in key_list:
        value = read_tuple_from_yaml(yaml_path, key)
        if value is not None:
            rectangles.append(value)
        else:
            print(f"键 {key} 不存在。")

    draw_multiple_rectangles_and_save(image_path, rectangles, save_path)


if __name__ == '__main__':

    pk_platform = 'wpk'
    max_players = 8
    room_yaml = f"{pk_platform}{max_players}.yaml"            
    room_yaml_path = get_file_full_name(room_yaml, 'data', 'input', 'table_setup')
    
    # 读取路径
    image_number = input("Please enter the image number: ")
    image_name = f"{image_number}.png"  
    image_path = get_file_full_name(image_name, 'data', 'test')

    # 保存路径
    filename = f"{image_number}_new.png"
    save_path = get_file_full_name(filename, 'data', 'test')

    
    main(image_path, save_path, room_yaml_path)



