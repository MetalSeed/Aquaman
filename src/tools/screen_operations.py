import datetime
import time
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw

# 窗口检测器
class WindowMonitor:
    def __init__(self, window_title):
        self.window_title = window_title
        self.window = None

    def find_window(self):
        """查找并绑定指定标题的窗口"""
        windows = gw.getWindowsWithTitle(self.window_title)
        self.window = windows[0] if windows else None
        return self.window is not None

    def is_window_valid(self):
        """检查窗口是否未被遮挡且不是最小化状态"""
        if self.window is None or not self.window.isActive or self.window.isMinimized:
            return False
        return True

    def wait_for_window(self):
        """等待窗口出现并进入有效状态"""
        print(f"Waiting for window '{self.window_title}' to become available...")
        while not self.find_window() or not self.is_window_valid():
            print(f"Window '{self.window_title}' is not available yet.")
            time.sleep(1)

# 窗口截图工具
class ScreenshotUtil:
    def __init__(self, window_title):
        self.window_monitor = WindowMonitor(window_title)

    def capture_screen(self):
        self.window_monitor.find_window()
        window = self.window_monitor.window
        if window:
            if not self.window_monitor.is_window_valid():
                self.window_monitor.wait_for_window()
            # 使用pyautogui截取指定窗口区域的屏幕
            window_bbox = window.box
            screenshot = pyautogui.screenshot(region=window_bbox)
            return screenshot
        else:
            print(f"Window '{self.window_monitor.window_title}' not found.")
            return None
    # screenshot 是截图的PIL, template是用cv2.read()
    def match_template_in_screenshot(self, screenshot, template, region, threshold=0.8):
        """在截图中的指定区域寻找模板图片"""
        if screenshot is None:
            print("Invalid screenshot.")
            return False
        if region:
            screenshot = screenshot.crop(region)  # PIL Image.crop expects a tuple (left, upper, right, lower)
        screenshot_np = np.array(screenshot) # 将PIL图像转换为numpy数组
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY) # 转换颜色空间
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) # 转换颜色空间

        th, tw = template_gray.shape[:2]
        # 获取截图的高度和宽度
        sh, sw = screenshot_gray.shape[:2]
        # 检查模板是否比截图大
        if th > sh or tw > sw:
            print("模板图像的尺寸超过了截图的尺寸，无法进行匹配。")
            return False

        res = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        return len(loc[0]) > 0  # 如果找到模板，返回 True；否则，返回 False

    def save_screenshot(self, screenshot, save_path=None):
        """保存截图"""
        if save_path is None:
            now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            save_path = f"{now}.png"
        screenshot.save(save_path)
        return save_path
    