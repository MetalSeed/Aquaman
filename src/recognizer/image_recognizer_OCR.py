import re
import cv2
import numpy as np
import pytesseract

class GameOCR:
    def __init__(self):
        # 花色识别阈值
        self.effective_pixel_ratio = 0.01 # 掩码中有效像素比例
        self.pocker_color_ranges = {}
        self.status_color_ranges = {}

    def check_color_presence(self, mask, image_area):
        # 计算掩码中非零像素的比例
        non_zero_count = cv2.countNonZero(mask)
        ratio = non_zero_count / image_area
        # 如果非零像素的比例大于阈值，则认为该颜色存在
        return ratio
    
    # 识别扑克牌的花色 - 四色扑克
    def recognize_suit(self, img):
        image_array = np.array(img)
        hsv = cv2.cvtColor(image_array, cv2.COLOR_BGR2HSV)
        image_area = image_array.shape[0] * image_array.shape[1]

        for suit, (lower, upper) in self.pocker_color_ranges.items():
            lower = np.array(lower, dtype="uint8")
            upper = np.array(upper, dtype="uint8")
            mask = cv2.inRange(hsv, lower, upper)

            # 如果颜色比例足够，则返回花色
            ratio = self.check_color_presence(mask, image_area)
            # print(f"{suit} ratio: {ratio}")
            if  ratio > self.effective_pixel_ratio:
                return suit
            
        print("花色未识别")
        return None

    # 文字识别图像预处理, 
    def preprocess_image(self, image):
        img = np.array(image) # img是cv2.imread()读取的图像 或者PIL转成numpy
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 应用高斯模糊
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # 应用二值化
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    # 识别图像中的点数
    def recognize_rank(self, img):
        image_array = np.array(img)
        # 预处理图像
        preprocessed_img = self.preprocess_image(image_array)
        # OCR配置：不限制字符集，适合识别点数
        custom_config = r'--oem 3 --psm 7'
        rank_text = pytesseract.image_to_string(preprocessed_img, config=custom_config)
        rank_text = rank_text.strip()  # 去除前后空格
        # print(f"rank_text: {rank_text}")
        
        # 后处理：校正常见的识别错误和“10”的特殊情况
        corrected_rank = rank_text.replace('IO', '10').replace('I0', '10').replace('1O', '10')
        corrected_rank = rank_text.replace('is}', 'Q')

        # 验证点数是否有效
        valid_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        if corrected_rank in valid_ranks:
            return corrected_rank
        else:
            print("点数未识别")
            return None

    # 识别扑克牌
    def recognize_poker_card(self, img_rank, img_suit):

        # 使用 recognize_suit 函数识别花色
        suit = self.recognize_suit(img_suit)
        
        # 调用 recognize_rank 函数识别点数
        rank = self.recognize_rank(img_rank)
        
        # 组合点数和花色
        result = f'{rank}{suit}' if suit and rank else None
        return result
       
    # 识别图像中的数字
    def recognize_digits(self, img):
        # 预处理图像
        preprocessed_img = self.preprocess_image(img)
        # 配置Tesseract以仅识别数字
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
        # 使用Tesseract OCR识别数字
        digits = pytesseract.image_to_string(preprocessed_img, config=custom_config)
        if digits.strip() == "":
            return None
        else:
            return digits.strip()

    # 识别图像中的字符串
    def recognize_string(self, img):
        # 预处理图像
        preprocessed_img = self.preprocess_image(img)
        # 使用Tesseract OCR识别字符串
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist="BetRaiseCheckCallFold"'
        # custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
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

        for suit, (lower, upper) in self.status_color_ranges.items():
            lower = np.array(lower, dtype="uint8")
            upper = np.array(upper, dtype="uint8")
            mask = cv2.inRange(hsv, lower, upper)

            # 如果颜色比例足够，并且最大轮廓足够大，则返回花色
            if self.check_color_presence(mask):
                largest_contour = self.find_largest_contour(mask)
                if largest_contour and self.is_contour_large_enough(largest_contour, image_area):
                    return suit
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
    
