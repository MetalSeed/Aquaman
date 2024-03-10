import os
import re
import sys
import time
from PIL import Image
import cv2
import numpy as np
import pytesseract


###############################
#       添加项目根目录          #        
###############################
import os
import sys
# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(grandparent_dir)
###############################
#       debug config          #
###############################
is_debug_print = False
is_debug_save = False

from src.tools.aqm_utils import get_file_full_name
import datetime


class ImageRecognizer:
    def __init__(self):
        # 花色识别阈值
        self.color_ranges_pocker = {}
        self.status_color_ranges = {}
        self.other_color_ranges = {}
        self.threshold_color_diff_poker_background = 30 # 判断是否有文字
        self.threshold_color_diff_text_background = 30 # 判断是否有文字
        self.threshold_color_match_poker = 0.2 # 判断花色
        self.threshold_binary_white_text = 100 # 浅色字体二值化阈值
        

    def check_color_presence(self, mask, image_area):
        # 计算掩码中非零像素的比例
        non_zero_count = cv2.countNonZero(mask)
        ratio = non_zero_count / image_area
        # 如果非零像素的比例大于阈值，则认为该颜色存在
        return ratio
    
        # color matching
    def color_matching(self, croped_img, color_ranges, color_ratio_threshold):
        image_array = np.array(croped_img)
        hsv = cv2.cvtColor(image_array, cv2.COLOR_BGR2HSV)
        image_area = image_array.shape[0] * image_array.shape[1]

        for colorname, (lower, upper) in color_ranges.items():
            lower = np.array(lower, dtype="uint8")
            upper = np.array(upper, dtype="uint8")
            mask = cv2.inRange(hsv, lower, upper)
            # 如果颜色比例足够，则返回花色
            ratio = self.check_color_presence(mask, image_area)
            if is_debug_print: print(f"{colorname} ratio: {round(ratio, 2)}") # debug print
            if ratio > color_ratio_threshold:
                basic_colorname = colorname.split('1')[0].split('2')[0].split('3')[0]
                return basic_colorname

        print(f"color matching failed")
        return None
    
    # 识别扑克牌的花色 - 四色扑克
    def recognize_suit(self, img, color_ratio_threshold):
        suit = self.color_matching(img, self.color_ranges_pocker, color_ratio_threshold)
        if not suit:
            print("花色未识别")
            return None
        return suit

    def preprocess_image(self, image, lighttext = True, threshold_binary=100, binarize=True):
        if lighttext: basewidth = 300
        else: basewidth = 100
        wpercent = (basewidth / float(image.size[0]))
        hsize = int((float(image.size[1]) * float(wpercent)))
        img_resized = image.convert('L').resize((basewidth, hsize), Image.LANCZOS)
        if binarize:
            """Binarize image from gray channel with 76 as threshold"""
            img = cv2.cvtColor(np.array(img_resized), cv2.COLOR_BGR2RGB)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # 应用高斯模糊
            blur = cv2.GaussianBlur(img, (5, 5), 0)
            if lighttext: # 浅色字体，深色背景，cv2.THRESH_BINARY_INV 反转二进制
                _, thresh = cv2.threshold(blur, threshold_binary, 255, cv2.THRESH_BINARY_INV) 
            else: # 深色字体，浅色背景 自适应二值化阈值
                _, thresh = cv2.threshold(blur, threshold_binary, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) 
            img_resized = thresh
        if is_debug_save:
            # 保存在data/test目录下
            current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"{current_time}.png"
            savepath = get_file_full_name(filename, 'data', 'test')
            # Save the image
            cv2.imwrite(savepath, img_resized)
            time.sleep(2)
        return img_resized
    
    # 识别图像中的点数
    def recognize_rank(self, img):
        # 预处理图像
        preprocessed_img = self.preprocess_image(img, False)
        # OCR配置：不限制字符集，适合识别点数
        custom_config = r'--oem 3 --psm 10'
        rank_text = pytesseract.image_to_string(preprocessed_img, config=custom_config)
        rank_text = rank_text.strip()  # 去除前后空格
        if is_debug_print: print(f"# Card_rank #: {rank_text}")
        
        # 后处理：校正常见的识别错误和“10”的特殊情况
        corrected_rank = rank_text.replace('IO', '10').replace('I0', '10').replace('1O', '10').replace('0', '10').replace('O', '9')
        # 验证点数是否有效
        valid_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        if corrected_rank in valid_ranks:
            return corrected_rank
        else:
            print("点数未识别")
            return None

    def detect_text_by_color_difference(self, img, std_dev_threshold):
        img = np.array(img)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # 计算每个通道的标准差
        std_dev = np.std(hsv_img, axis=(0, 1))
        max_std_dev = "{:.0f}".format(np.max(std_dev))
        # 检查标准差是否超过阈值，超过则可能表示存在文字 
        if np.any(std_dev > std_dev_threshold):
            if is_debug_print: print(f"# Color_diff #: {std_dev_threshold}:{max_std_dev} have text")
            return True
        else:
            if is_debug_print: print(f"# Color_diff #: {std_dev_threshold}:{max_std_dev}  no  text")
            return False
    
    # 识别扑克牌
    def recognize_poker_card(self, img_rank, img_suit):

        threshold_text = self.detect_text_by_color_difference(img_rank, self.threshold_color_diff_poker_background)
        if threshold_text is False:
            # print("No text detected in rank")
            return None

        # 使用 recognize_suit 函数识别花色
        suit = self.recognize_suit(img_suit, self.threshold_color_match_poker)
        
        # 调用 recognize_rank 函数识别点数
        rank = self.recognize_rank(img_rank)
        
        # 组合点数和花色
        result = f'{rank}{suit}' if suit and rank else None
        return result
       

    # 识别图像中的数字
    def recognize_digits(self, img):
        threshold_text = self.detect_text_by_color_difference(img, self.threshold_color_diff_text_background)
        if threshold_text is False: return None
        """New OCR based on tesserocr rather than pytesseract, should be much faster"""
        # 预处理图像
        preprocessed_img = self.preprocess_image(img, True, self.threshold_binary_white_text)
        # 配置Tesseract以仅识别数字
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.$£B'
        # 使用Tesseract OCR识别数字
        digits = pytesseract.image_to_string(preprocessed_img, config=custom_config)
        
        digits = digits.strip() # 去除前后空格
        digits.replace('$', '').replace('£', '').replace('€', '').replace('B', '').replace(',', '.').replace('\n', '').replace(':','') # replace

        if digits == "":
            return None
        else:
            return digits

    # 识别图像中的字符串
    def recognize_string(self, img):
        threshold_text = self.detect_text_by_color_difference(img, self.threshold_color_diff_text_background)
        if threshold_text is False: return None
        # 预处理图像
        preprocessed_img = self.preprocess_image(img, True, self.threshold_binary_white_text)
        # 使用Tesseract OCR识别字符串
        custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist="BetRaiseCheckCallFold"'
        string = pytesseract.image_to_string(preprocessed_img, config=custom_config)
        return string.strip()

    def correct_ocr_errors_and_match_terms(self, ocr_result):
        terms = ["Bet", "Raise", "Check", "Call", "Fold"]
        # 定义替换规则来修正常见的OCR错误
        corrections = {
            '0': 'o',  # 或 'O' 根据上下文
            '1': 'l',  # 或 'I' 或 'i' 根据上下文
            '5': 's',  # 或 'S'
            '8': 'B',
            'l': 'I',  # 或 '1' 根据上下文
            # 添加更多的替换规则
        }
        
        # 对OCR结果应用替换规则
        for wrong, correct in corrections.items():
            ocr_result = re.sub(wrong, correct, ocr_result, flags=re.IGNORECASE)

        # 将OCR结果与预定义的术语列表进行匹配
        matched_term = None
        for term in terms:
            # 使用正则表达式进行不区分大小写的匹配
            if re.fullmatch(term, ocr_result, re.IGNORECASE):
                matched_term = term
                break
        
        # 如果匹配到预定义的术语，则返回该术语，否则返回"其他"
        return matched_term.capitalize() if matched_term else "others"

    # 识别状态颜色
    def recognize_status_color(self, img):

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        image_area = img.shape[0] * img.shape[1]

        for state, (lower, upper) in self.status_color_ranges.items():
            lower = np.array(lower, dtype="uint8")
            upper = np.array(upper, dtype="uint8")
            mask = cv2.inRange(hsv, lower, upper)

            # 如果颜色比例足够，则返回花色
            ratio = self.check_color_presence(mask, image_area)
            # print(f"{state} ratio: {ratio}")
            if  ratio > self.effective_pixel_ratio:
                return state

        return None
    
    # 识别状态
    def recognize_status(self, img):
        ocr_string = self.recognize_string(img)
        status_string = self.correct_ocr_errors_and_match_terms(ocr_string)
        status_color = self.recognize_status_color(img)

        if status_color == 'b' and status_string == 'Bet':
            return 'Bet'
        elif status_color == 'r' and status_string == 'Raise':
            return 'Raise'
        elif status_color == 'x' and status_string == 'Check':
            return 'Check'
        elif status_color == 'c' and status_string == 'Call':
            return 'Call'
        elif status_color == 'f' and status_string == 'Fold':
            return 'Fold'
        else:
            return 'others'
    