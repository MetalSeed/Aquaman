# 通用函数工具

import os

# file_full_name = get_file_full_name('1.jpg', 2, 'data', 'output', 'table_setup')
def get_file_full_name(file_name, up_levels, *subfolders):
    # 获取当前脚本的绝对路径
    script_dir = os.path.dirname(__file__)
    
    # 根据指定的层数向上遍历获取父目录
    for _ in range(up_levels):
        script_dir = os.path.dirname(script_dir)
    
    # 最终的父目录即为向上遍历后的结果
    final_dir = script_dir

    # 构建目标文件的绝对路径，包括可变数量的子文件夹路径
    file_full_name = os.path.join(final_dir, *subfolders, file_name)
    return file_full_name
