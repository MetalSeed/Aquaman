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

# 往yaml文件写入或更新数据，value可以是值，字符串，也可以是List
def update_or_add_to_yaml(file_path, keys, value):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        data = {}

    # 更新或添加键值对
    action = update_nested_dict(data, keys, value)

    # 将更新后的数据写回YAML文件
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False)
    
    return action

# # 要写入/更新的数据
# key = 'P0_status'
# value = [289, 383, 422, 484]  # YAML没有元组，使用列表代替

# # 执行更新或添加操作
# action = update_or_add_to_yaml('config.yaml', key, value)
# print(f"操作结果：{action}")


# key是列表，就返回列表，key是健，就返回值
def read_value_from_yaml(file_path, key):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    value = data.get(key)
    if value is not None:
        return value
    else:
        print(f"键 {key} 不存在。")
        return None

def read_tuple_from_yaml(file_path, key):
    value = read_value_from_yaml(file_path, key)
    if value is not None:
        return tuple(value)  # 将列表转换为元组
    else:
        print(f"键 {key} 不存在。")
        return None


def fill_dict_from_yaml(config_dict, yaml_path):
    # 从YAML文件读取数据
    with open(yaml_path, 'r', encoding='utf-8') as file:
        yaml_data = yaml.load(file, Loader=yaml.FullLoader)
    
    # 遍历配置字典中的键，并尝试从YAML数据中填充值
    for key in config_dict.keys():
        if key in yaml_data:
            config_dict[key] = yaml_data[key]
    
    return config_dict

# # 使用示例

# config_template = {
#     'window_title': None,
#     'platform': None,
#     'max_players': None,
#     'big_blind': None,
#     'small_blind': None,
#     }

# yaml_path = 'config.yaml'  # 假设你的YAML文件名为config.yaml
# filled_config = fill_dict_from_yaml(config_template, yaml_path)
# print(filled_config)



    