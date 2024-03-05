import yaml

def update_nested_dict(dct, keys, value):
    """
    递归更新嵌套字典
    :param dct: 当前字典
    :param keys: 键的列表，表示更新路径 keys = ['config', 'database', 'port']，单个字符串要转换成列表 my_list = [my_string]
    :param value: 要设置的值
    :return: 更新操作的类型（"新增", "更新", "无变化"）
    """
    key = keys[0]
    if len(keys) == 1:
        if dct.get(key) == value:
            return "无变化"
        elif key in dct:
            dct[key] = value
            return "更新"
        else:
            dct[key] = value
            return "新增"
    else:
        if key not in dct:
            dct[key] = {}
        return update_nested_dict(dct[key], keys[1:], value)

# 往yaml文件写入或更新数据
def update_or_add_to_yaml(file_path, keys, value):
    try:
        with open(file_path, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        data = {}

    # 更新或添加键值对
    action = update_nested_dict(data, keys, value)

    # 将更新后的数据写回YAML文件
    with open(file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)
    
    return action

# # 要写入/更新的数据
# key = 'P0_status'
# value = [289, 383, 422, 484]  # YAML没有元组，使用列表代替

# # 执行更新或添加操作
# action = update_or_add_to_yaml('config.yaml', key, value)
# print(f"操作结果：{action}")



def read_tuple_from_yaml(file_path, key):
    with open(file_path, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    value = data.get(key)
    if value is not None:
        return tuple(value)  # 将列表转换为元组
    else:
        return None

# # 从YAML文件读取P0_status并赋值给P0_status1
# P0_status1 = read_tuple_from_yaml('config.yaml', 'P0_status')
# print(f"P0_status1: {P0_status1}")
    


# 分成写列表和写字典两个函数？ 测试一下直接写列表回怎样