import os
import re
import sys
import time
from PIL import Image
import cv2
import numpy as np
import pytesseract

import logging
# 配置日志格式，包括时间、日志级别、文件名、所处函数名、所在行数和消息
# 使用括号将格式字符串分成多行，以提高可读性
logging.basicConfig(format=(
    '%(asctime)s - %(levelname)s - '
    '[%(filename)s - %(funcName)s - Line %(lineno)d]: '
    '%(message)s'
), level=logging.WARNING)


# 特定bug之后，把原图，预处理，结果都保存下来
processed_img_save = False

# 为特定模块获取一个日志器
logger = logging.getLogger('moduleName')
logger.setLevel(logging.WARNING)  # 为这个日志器设置级别

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
        
# 预处理部分
    # auto_threshold: 自动二值化阈值  当图像的字体与背景分散在两极时，自适应比较方便。当背景色分散在两极时，截图范围大了会有bug，可以用手动值来解决
    def preprocess_image(self, image, auto_threshold = True, threshold_binary=100, binarize=True, name = None):
        if auto_threshold:
            basewidth = 100
        else:
            basewidth = 300

        wpercent = (basewidth / float(image.size[0]))
        hsize = int((float(image.size[1]) * float(wpercent)))
        img_resized = image.convert('L').resize((basewidth, hsize), Image.LANCZOS)
        if binarize:
            """Binarize image from gray channel with 76 as threshold"""
            img = cv2.cvtColor(np.array(img_resized), cv2.COLOR_BGR2RGB)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # 应用高斯模糊
            blur = cv2.GaussianBlur(img, (5, 5), 0)
            if auto_threshold:  # 自适应二值化阈值，适用于颜色单一的情况
                _, thresh = cv2.threshold(blur, threshold_binary, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) 
            else:  # 白色字体，适用于所有背景都是偏暗色的的情况，cv2.THRESH_BINARY_INV 反转二进制 变成黑色字体
                _, thresh = cv2.threshold(blur, threshold_binary, 255, cv2.THRESH_BINARY_INV) 

            img_resized = thresh
        if processed_img_save:
            # 保存在data/test目录下
            current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"{name}{current_time}.png"
            savepath = get_file_full_name(filename, 'data', 'test')
            # Save the image
            cv2.imwrite(savepath, img_resized)
            time.sleep(2)
        return img_resized

    def detect_text_by_color_difference(self, img, std_dev_threshold):
        img = np.array(img)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # 计算每个通道的标准差
        std_dev = np.std(hsv_img, axis=(0, 1))
        max_std_dev = "{:.0f}".format(np.max(std_dev))
        # 检查标准差是否超过阈值，超过则可能表示存在文字 
        if np.any(std_dev > std_dev_threshold):
            logger.debug(f"# Color_diff #: {std_dev_threshold}:{max_std_dev} have text")
            return True
        else:
            logging.debug(f"# Color_diff #: {std_dev_threshold}:{max_std_dev}  no  text")
            return False
    

       
# OCR 部分
    # 识别图像中的点数
    def recognize_rank(self, img):
        # 预处理图像
        preprocessed_img = self.preprocess_image(img, True, name = 'rank')
        # psm 8: word mode, psm 10: single character mode, psm 7: a single line of text
        custom_config = r'--psm 8 -c tessedit_char_whitelist=0123456789AJQK'
        rank_text = pytesseract.image_to_string(preprocessed_img, config=custom_config)
        rank_text = rank_text.strip()  # 去除前后空格
        
        rank = self.corrector_poker_rank(rank_text)
        return rank
    
    # 识别图像中的数字
    def recognize_digits(self, img):
        threshold_text = self.detect_text_by_color_difference(img, self.threshold_color_diff_text_background)
        if threshold_text is False: return None
        """New OCR based on tesserocr rather than pytesseract, should be much faster"""
        # 预处理图像 以前版本是auto_threshold是False 自动二值化会在没有数字的情况下误识别
        preprocessed_img = self.preprocess_image(img, False, self.threshold_binary_white_text, name = 'digits')
        # 配置Tesseract以仅识别数字
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.$£B'
        # 使用Tesseract OCR识别数字
        digits = pytesseract.image_to_string(preprocessed_img, config=custom_config)
        digits = digits.strip() # 去除前后空格

        digits = self.corrector_digits(digits)
        return digits

    # 识别图像中的字符串, 自动二值化阈值 
    def recognize_decision_string(self, img, auto_threshold = True):
        threshold_text = self.detect_text_by_color_difference(img, self.threshold_color_diff_text_background)
        if threshold_text is False: return None
        # 预处理图像
        preprocessed_img = self.preprocess_image(img, auto_threshold, self.threshold_binary_white_text, name = 'string')
        # 使用Tesseract OCR识别字符串
        custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist="BetRaiseCheckCallFoldAllin"'
        string = pytesseract.image_to_string(preprocessed_img, config=custom_config)
        return string.strip()

    # 识别图像中的黑色数字
    def recognize_black_digits(self, img):
        preprocessed_img = self.preprocess_image(img, True, self.threshold_binary_white_text)
        # 使用Tesseract OCR识别字符串
        custom_config = r'--oem 3 --psm 6 outputbase digits'
        string = pytesseract.image_to_string(preprocessed_img, config=custom_config)
        return string.strip()
    

# OCR corrector 部分
    def corrector_poker_rank(self):
        raise NotImplementedError("Subclass must implement abstract method")
    
    def corrector_digits(self, digits):
        # if not digits:
        #     return None
        
        if digits == "":
            return None
        
        # digits = digits.replace('B', '8').replace('O', '0').replace('o', '0').replace('S', '5').replace('s', '5').replace('Z', '2').replace('z', '2').replace('I', '1').replace('l', '1').replace('i', '1')
        digits.replace('$', '').replace('£', '').replace('€', '').replace('B', '').replace(',', '.').replace('\n', '').replace(':','') # replace
        return digits


# 最终 recoginzer部分
    
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
        if result is None:
            logger.warning(f"# Poker rank : {rank} ## Poker suit : {suit}")
        return result
    
    # 识别扑克牌的花色 - 四色扑克
    def recognize_suit(self, img, color_ratio_threshold):
        suit = self.color_matching(img, self.color_ranges_pocker, color_ratio_threshold)
        if not suit:
            logger.debug("花色未识别")
            return None
        return suit


# 颜色匹配部分
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
            logger.info(f"{colorname} ratio: {round(ratio, 2)}") # debug print
            if ratio > color_ratio_threshold:
                basic_colorname = colorname.split('1')[0].split('2')[0].split('3')[0]
                return basic_colorname
        logger.debug(f"color matching failed")
        return None