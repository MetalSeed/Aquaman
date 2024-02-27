import cv2
import numpy as np
import pytesseract

class BasicOCR:
    def __init__(self):
        # 花色识别阈值
        self.effective_pixel_ratio = 0.01 # 掩码中有效像素比例
        self.contour_area_ratio = 0.01 # 最大轮廓面积比例
        self.color_ranges = {}

    def check_color_presence(self, mask):
        # 计算掩码中非零像素的比例
        height, width = mask.shape[:2]
        non_zero_count = cv2.countNonZero(mask)
        total_count = height * width
        ratio = non_zero_count / total_count
        # 如果非零像素的比例大于阈值，则认为该颜色存在
        return ratio > self.effective_pixel_ratio

    def find_largest_contour(self, mask):
        # 在掩码中找到最大的轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            return largest_contour
        return None

    def is_contour_large_enough(self, contour, image_area, ):
        # 判断轮廓是否足够大
        contour_area = cv2.contourArea(contour)
        return (contour_area / image_area) > self.contour_area_ratio


    # 文字识别图像预处理, img是cv2.imread()读取的图像
    def preprocess_image(self, image):
        # 读取图像
        img = image
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 应用高斯模糊
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # 应用二值化
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh


    # 识别图像中的数字
    def recognize_digits(self, img):
        # 预处理图像
        preprocessed_img = self.preprocess_image(img)
        # 配置Tesseract以仅识别数字
        custom_config = r'--oem 3 --psm 6 outputbase digits'
        # 使用Tesseract OCR识别数字
        digits = pytesseract.image_to_string(preprocessed_img, config=custom_config)
        return digits.strip()

    # 识别扑克牌的花色 - 四色扑克
    def recognize_suit(self, img):

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        image_area = img.shape[0] * img.shape[1]

        for suit, (lower, upper) in self.color_ranges.items():
            lower = np.array(lower, dtype="uint8")
            upper = np.array(upper, dtype="uint8")
            mask = cv2.inRange(hsv, lower, upper)

            # 如果颜色比例足够，并且最大轮廓足够大，则返回花色
            if self.check_color_presence(mask):
                largest_contour = self.find_largest_contour(mask)
                if largest_contour and self.is_contour_large_enough(largest_contour, image_area):
                    return suit
        return None
    
    # 识别图像中的点数
    def recognize_rank(self, img):
        # 预处理图像
        preprocessed_img = self.preprocess_image(img)
        # OCR配置：不限制字符集，适合识别点数
        custom_config = r'--oem 3 --psm 6'
        rank_text = pytesseract.image_to_string(preprocessed_img, config=custom_config)
        rank_text = rank_text.strip()  # 去除前后空格
        
        # 后处理：校正常见的识别错误和“10”的特殊情况
        corrected_rank = rank_text.replace('IO', '10').replace('I0', '10').replace('1O', '10')
        
        # 验证点数是否有效
        valid_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        if corrected_rank in valid_ranks:
            return corrected_rank
        else:
            return '识别不确定'

    # img是cv2.imread()的图像
    def recognize_poker_card(self, img_rank, img_suit):

        # 使用 recognize_suit 函数识别花色
        suit = self.recognize_suit(img_suit)
        
        # 调用 recognize_rank 函数识别点数
        rank = self.recognize_rank(img_rank)
        
        # 组合点数和花色
        result = f'{rank}{suit}' if suit and rank not in ['未能识别', '识别不确定'] else '未能识别'
        return result
       

class WePokerOCR(BasicOCR):
    def __init__(self):
        super().__init__()  # 调用父类的初始化方法
        self.effective_pixel_ratio = 0.10 # 花色识别中，掩码中有效像素比例
        self.contour_area_ratio = 0.10 # 花色识别中，最大轮廓面积比例
        # 定义四种花色的HSV颜色范围
        self.color_ranges = {
            'c': ([36, 25, 25], [86, 255,255]),  # 绿色
            'h': ([0, 150, 50], [10, 255, 255]),  # 红色
            's': ([0, 0, 0], [180, 255, 30]),     # 黑色
            'd': ([94, 80, 2], [126, 255, 255]),  # 蓝色
        }

    
# 调用函数
image_path = 'path/to/your/poker_card.jpg'
image = cv2.imread(image_path)
img_suit = image[0:30, 0:30]  # 花色区域
img_rank = image[30:60, 0:30]  # 点数区域

result = WePokerOCR.recognize_poker_card(img_rank, img_suit)
print("识别结果：", result)

# 使用示例
image_path = 'path/to/your/image.jpg'
image = cv2.imread(image_path)
recognized_digits = WePokerOCR.recognize_digits(image)
print("识别的数字：", recognized_digits)