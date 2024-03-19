
# 获得第一张截图，用来获得 tables_collector 检测图和检测坐标

import sys
import pygetwindow as gw
import pyautogui
import datetime
import time
import os

# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(grandparent_dir)

from src.tools.aqm_utils import get_file_full_name

# 每隔2s截图一张
def capture_windowshot(window_title):
    try:
        # 查找并获取窗口
        window = gw.getWindowsWithTitle(window_title)[0]
        if window:
            while True:
                # 获取当前时间作为文件名
                now = datetime.datetime.now()
                filename = now.strftime("%Y%m%d%H%M%S") + ".png"
                filepath = get_file_full_name(filename, "data", "test")

                window.activate() # 确保窗口是激活的
                time.sleep(1) # 等待窗口被激活，可能需要根据实际情况调整等待时间

                # 截图并保存
                screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
                screenshot.save(filepath)
                print(f"截图已保存至：{filepath}")

                # 等待5秒再次截图
                time.sleep(2)
        else:
            print("未找到指定的窗口。")
    except Exception as e:
        print(f"发生错误: {e}")

# 使用示例, 获取第一个截图
window_title = "雷电模拟器"  # 修改为你的窗口标题
capture_windowshot(window_title)


