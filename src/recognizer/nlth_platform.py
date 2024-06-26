# shoter & 平台属性层
import os
import re
import sys
import time
import cv2
import numpy as np

import logging
# 配置日志格式，包括时间、日志级别、文件名、所处函数名、所在行数和消息
# 使用括号将格式字符串分成多行，以提高可读性
logging.basicConfig(format=(
    '%(asctime)s - %(levelname)s - '
    '[%(filename)s - %(funcName)s - Line %(lineno)d]: '
    '%(message)s'
), level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(grandparent_dir)


from src.recognizer.image_recognizer import ImageRecognizer
from src.tools.screen_operations import ScreenshotUtil
from loadconfig import filled_room_config, filled_room_rects, template_dir


class RoomRecognizer(ImageRecognizer):
    def __init__(self):
        ImageRecognizer.__init__(self)
        self.max_players = filled_room_config['max_players']
        self.window_title = filled_room_config['window_title']
        self.windowshoter = ScreenshotUtil(self.window_title)
        self.windowshot = None
        # 颜色匹配中的比例
        self.threshold_color_match_decision = 0.1 # 花色识别中，掩码中有效像素比例
        self.threshold_color_match_hero_turn = 0.1 # hero回合标志颜色比例
        self.threshold_color_match_have_cards = 0.1 # 是否存活颜色比例
        self.threshold_color_match_is_empty_seat = 0.1 # 是否有玩家比例

    def takeshot(self):
        self.windowshot = self.windowshoter.capture_screen()
        if self.windowshot is None:
            print("截图失败")
            return False
        else:
            return True
        
    # 捕捉heron行动回合截图
    def heroturnshot(self):
        start_time = time.time()  # 记录开始时间
        while self.takeshot():
            if self.is_hero_turn():
                time.sleep(1) # 更新截图 避开动画 耗时
                self.takeshot() # 更新截图 避开动画 耗时
                return True
            else:
                self.windowshot = None
                # print("不是hero的回合")
                time.sleep(1)
                if time.time() - start_time > 300:  # 超过200秒
                    print(f"table_shoter，超过300秒没轮到hero")
                    return None

    # 图像匹配精度 0.9 要求高
    def image_matching(self, template_path, region):
        template_image = cv2.imread(template_path)
        if template_image is None:
            print(f"template: {template_path}不存在")
            return None
        result = self.windowshoter.match_template_in_screenshot(self.windowshot, template_image, region, threshold=0.9)
        return result

    def is_hero_turn_color_matching(self):
        croped_img = self.windowshot.crop(filled_room_rects['hero_fold'])
        result = self.color_matching(croped_img, self.color_ranges_hero_turn, self.threshold_color_match_hero_turn)
        if result == 'red':
            return True
        else:
            logger.debug("不是hero的回合")
            return False
    
    def is_hero_turn_tempate_matching(self):
        # mode 1: 
        file_path = os.path.join(template_dir, 'is_hero_turn.png')
        result = self.image_matching(file_path, filled_room_rects['hero_turn'])
        if result:
            return True
        else:
            return False
    def is_hero_turn(self, mode=2): # 默认使用颜色
        if mode == 1: # mode 1: 模板匹配
            result = self.is_hero_turn_tempate_matching()
        elif mode == 2: # mode 2: 颜色匹配
            result = self.is_hero_turn_color_matching()
        if result:
            return True
        else:
            return False

    # 桌面信息检测
    # 桌面信息检测
    # 桌面信息检测
    def get_dealer_abs_position(self):
        dap = None
        for i in range(self.max_players):
            file_path = os.path.join(template_dir, 'dealer.png')
            result = self.image_matching(file_path, filled_room_rects[f'P{i}_dealer'])
            if result:
                dap = i
                break
        return dap
    
    def get_number(self, key):
        number = None
        img = self.windowshot.crop(filled_room_rects[key])
        number = self.recognize_digits(img)
        return number

    def get_last_round_pot(self):
        return self.get_number('pot_last_round')

    def get_total_pot(self):
        return self.get_number('pot_total')
    
    def get_public_cards(self):
        public_cards = []
        img_rank = None
        img_suit = None
        for i in range(5):
            img_rank = self.windowshot.crop(filled_room_rects[f'board{i+1}_rank'])
            img_suit = self.windowshot.crop(filled_room_rects[f'board{i+1}_suit'])
            poker = self.recognize_poker_card(img_rank, img_suit)
            if poker:
                public_cards.append(poker)
            else:
                logger.info(f'公共牌{poker}识别失败')
                logger.info(f'公共牌{i+1}不存在')
                break
        return public_cards
    
    def get_hero_cards(self):
        hero_cards = []
        # 定义两张英雄卡牌的键名
        card_keys = [('hero_card1_rank', 'hero_card1_suit'), ('hero_card2_rank', 'hero_card2_suit')]
        
        for rank_key, suit_key in card_keys:
            img_rank = self.windowshot.crop(filled_room_rects[rank_key])
            img_suit = self.windowshot.crop(filled_room_rects[suit_key])
            poker = self.recognize_poker_card(img_rank, img_suit)
            if poker:
                hero_cards.append(poker)
            else:
                logger.error("识别hero牌失败")
        return hero_cards
    
    def get_have_cards(self, abs_position):
        croped_img = self.windowshot.crop(filled_room_rects[f'P{abs_position}_have_cards'])
        result = self.color_matching(croped_img, self.color_ranges_have_cards, self.threshold_color_match_have_cards)
        if result == 'pokerback':
            return True
        else: 
            logger.debug(f"P{abs_position}没有手牌")
            return False
    
    def get_player_pot(self, abs_position):
        pot = self.get_number(f'P{abs_position}_pot')
        if pot is None: 
            logger.debug(f"池底识别结果{pot}")
        return pot
    
    def get_player_funds(self, abs_position):
        funds = self.get_number(f'P{abs_position}_funds')
        if funds is None: 
            logger.debug(f"P{abs_position}资金识别结果 None")
        return funds

    def get_player_id(self, abs_position):
        ##########
        pass

    def get_call_value(self):
        return self.get_number('hero_call')

    def get_betX_balue(self, bet_level):
        bet_number = f'bet{bet_level}'
        return self.get_number(bet_number)

    def get_coordinates(self, key):
        x = int((filled_room_rects[key][0] + filled_room_rects[key][2]) / 2)
        y = int((filled_room_rects[key][1] + filled_room_rects[key][3]) / 2)
        return (int(x), int(y))
    
    def get_xy_player_photo(self, abs_position):
        return self.get_coordinates(f'P{abs_position}_photo')


    def get_xy_button(self, button_name):
        # 将button_name映射到对应的参数
        button_mapping = {
            'Call': 'hero_call',
            'Check': 'hero_call',
            'Fold': 'hero_fold',
            'Raise': 'hero_bet',
            'Bet1': 'bet1',
            'Bet2': 'bet2',
            'Bet3': 'bet3',
            'Bet4': 'bet4',
            'Bet5': 'bet5'
        }

        # 检查button_name是否存在于映射中
        if button_name in button_mapping:
            return self.get_coordinates(button_mapping[button_name])
        else:
            print(f"button_name: {button_name}不存在")
            return None


    # 状态监测部分
    # 状态监测部分
    # 状态监测部分
        
    def is_the_game_over(self):
        pass

    def is_hero_lost_all(self):
        pass

    def is_hero_short_funds(self):
        pass

    def is_empty_seat(self, abs_position):
        croped_img = self.windowshot.crop(filled_room_rects[f'P{abs_position}_photo'])
        result = self.color_matching(croped_img, self.color_ranges_empty_seat, self.threshold_color_match_is_empty_seat)
        if result == 'empty':
            return True
        else: 
            print(f"P{abs_position}没有玩家")
            return False
        
    # 房间状态检测
    def game_state_dectection(self):
        self.is_hero_lost_all()
        self.is_the_game_over()
        self.is_hero_short_funds()

    #
    # menu部分
    #
    def get_quit_coordinates(self):
        return self.get_coordinates('quit')


# wpk平台设置 4色牌 牌背红色 桌布绿色 
class wpkRR(RoomRecognizer):
    def __init__(self):
        RoomRecognizer.__init__(self)
        # 颜色匹配 颜色占比 阈值
        self.threshold_color_match_poker = 0.2 # 判断花色
        self.threshold_color_match_decision = 0.50 # 花色识别中，掩码中有效像素比例
        self.threshold_color_match_hero_turn = 0.3 # hero回合标志颜色比例
        self.threshold_color_match_have_cards = 0.3 # 是有手牌颜色比例
        self.threshold_color_match_is_empty_seat = 0.50 # 是否有玩家比例

        # 前后景区分度
        self.threshold_color_diff_poker_background = 30 # 判断是否有文字
        self.threshold_color_diff_text_background = 30 # 判断是否有文字

        # 文字识别
        self.threshold_binary_white_text = 100 # 浅色字体二值化阈值

        #############
        # 平台颜色范围#
        #############
        
        # 定义四种花色的HSV颜色范围 0.2
        self.color_ranges_pocker = {
            'c': ([56, 180, 150], [58, 241, 166]),  # 绿色 club
            'h': ([121, 160, 231], [122, 251, 239]),  # 红色 heart
            's': ([0, 0, 0],[60, 85, 28]),     # 黑色 spade
            'd': ([ 13, 184, 189], [ 15, 255, 206]),  # 蓝色 diamond
        }
        
        # check = green call = blue, raise = range, bet = green blue orange
        # 定义状态的HSV颜色范围 0.5
        self.color_ranges_decision = {
            'blue':  ([ 13, 168, 214], [ 17, 227, 239]), # bet call
            'orange': ([105, 127,  66], [110, 237, 239]), #raise orange
            'green': ([ 37, 146,  56], [ 43, 245, 207]), # check green
        }
        # 定义状态的HSV颜色范围 1or2 > 0.3
        self.color_ranges_hero_turn = {
            'red1':([122, 126, 222], [125, 211, 239]), # 亮红色
            'red2':([122, 95, 132], [126, 211, 148]),  # 暗红色
        }
        # 定义状态的HSV颜色范围 0.3
        self.color_ranges_have_cards = {
            'pokerback': ([117,  67, 198], [126, 135, 222]),  #红色
        }
        # 空座位 0.5空，0.3fold
        self.color_ranges_empty_seat = {
            'empty': ([150,   3,  33], [150,  39, 107]),  # 黑色
        }

    # 玩家的状态，check, call, bet, raise; fold, all-in，unknow
    def get_player_decision(self, abs_position):
        # name string, photo string, photo color, 
        decision = None
        croped_img_decision = self.windowshot.crop(filled_room_rects[f'P{abs_position}_decision'])
        
        decision_text = self.recognize_decision_string(croped_img_decision) 
        decision_text_corrected = self.ocr_corrector_decison(decision_text) # correct函数放在这里
        decision_color = self.color_matching(croped_img_decision, self.color_ranges_decision, self.threshold_color_match_decision)
        
        # check = green call = blue, raise = range, bet = green blue orange
        if decision_color in ['blue', 'orange', 'green']:
            if decision_text_corrected == 'Bet':
                decision = 'Bet'
            elif decision_color == 'orange':
                decision = 'Raise'
            elif decision_color == 'green':
                decision = 'Check'
            elif decision_color == 'blue':
                decision = 'Call'
            else:
                logger.error(f"P{abs_position} Raise or Bet 字符识别失败, 识别结果：{decision_text}, 矫正结果：{decision_text_corrected}")
                decision = 'Error'
        else:
            croped_img_photo = self.windowshot.crop(filled_room_rects[f'P{abs_position}_photo'])
            photo_text = self.recognize_decision_string(croped_img_photo) 
            photo_text_corrected = self.ocr_corrector_decison(photo_text) # correct函数放在这里
            if photo_text_corrected == 'Fold':
                decision = 'Fold'
            elif photo_text_corrected == 'Allin':
                decision = 'Allin'
            else:
                decision = 'unrec'
                logger.info(f"P{abs_position}状态识别结果：{photo_text}")
                logger.info(f"P{abs_position}状态矫正结果：{photo_text_corrected}")
        return decision
    
 # OCR corrector 部分
    def corrector_poker_rank(self, rank_text):
        logger.info(f"# Card_rank #: {rank_text}")
        # 矫正10的识别错误
        corrected_rank = rank_text.replace('IO', 'T').replace('I0', 'T').replace('1O', 'T').replace('10', 'T').replace('0', 'T')
        # 矫正Q的识别错误，注意用corrected_rank替换rank_text，否则会被替代
        corrected_rank = corrected_rank.replace('q', 'Q')
        
        # 验证点数是否有效
        valid_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        if corrected_rank in valid_ranks:
            return corrected_rank
        else:
            logger.warning(f"点数匹配出错 rank_text: {rank_text}, corrected_rank: {corrected_rank}")
            return None

    # OCR corrector
    def ocr_corrector_decison(self, ocr_result):
        ocr_text = ocr_result
        terms = ["Bet", "Raise", "Check", "Call", "Fold", 'Allin']
        # 定义替换规则来修正常见的OCR错误
        corrections = {
            '0': 'o',  # 或 'O' 根据上下文
            '1': 'l',  # 或 'I' 或 'i' 根据上下文
            '5': 's',  # 或 'S'
            '8': 'B',
        }
        
        # 对OCR结果应用替换规则
        for wrong, correct in corrections.items():
            ocr_result = re.sub(wrong, correct, ocr_result)
    
        # 处理特定的模式替换，比如Fo*都替换成Fold
        ocr_result = re.sub(r'\bFo[a-zA-Z]*\b', 'Fold', ocr_result)
        ocr_result = re.sub(r'\bAll[a-zA-Z]*\b', 'Allin', ocr_result)
        ocr_result = re.sub('Cail', 'Call', ocr_result)

        # 将OCR结果与预定义的术语列表进行匹配
        matched_term = None
        for term in terms:
            # 使用正则表达式进行匹配
            if re.fullmatch(term, ocr_result):
                matched_term = term
                break
        
        if not matched_term: logger.warning(f"decision矫正异常，ocr_text: {ocr_text}, 矫正后的结果：{ocr_result}")
        return matched_term.capitalize() if matched_term else "unknow"
    
    def windowshot_input(self, img):
        self.windowshot = img











