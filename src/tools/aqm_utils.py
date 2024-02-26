# 通用函数工具

import os

# 获取完整路径
def get_file_full_name(subf1, subf2, subf3, file_name):
    # 获取当前脚本的绝对路径
    script_dir = os.path.dirname(__file__)

    # 获取当前脚本的父目录的父目录
    grandparent_dir = os.path.dirname(os.path.dirname(script_dir))

    # 构建目标文件的绝对路径，包括子文件夹路径
    file_full_name = os.path.join(grandparent_dir, subf1, subf2, subf3, file_name)
    return file_full_name