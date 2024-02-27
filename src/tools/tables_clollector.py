# tableshots for table_setup or hands_converter

import pygetwindow as gw
import pyautogui
import datetime
import time
import os
from aqm_utils import get_file_full_name

def capture_window_screenshot(window_title):
    try:
        # 查找并获取窗口
        window = gw.getWindowsWithTitle(window_title)[0]
        if window:
            while True:
                # 获取当前时间作为文件名
                now = datetime.datetime.now()
                filename = now.strftime("%Y%m%d%H%M%S") + ".png"
                
                filepath = get_file_full_name(filename, 2, "data", "output", "tables_collector")

                # 确保窗口是激活的
                window.activate()
                # 等待窗口被激活，可能需要根据实际情况调整等待时间
                time.sleep(1)

                # 截图并保存
                screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
                screenshot.save(filepath)
                print(f"截图已保存至：{filepath}")

                # 等待1秒再次截图
                time.sleep(1)
        else:
            print("未找到指定的窗口。")
    except Exception as e:
        print(f"发生错误: {e}")

# 使用示例
window_title = "雷电模拟器-1"  # 修改为你的窗口标题


capture_window_screenshot(window_title)
