# shoter & 平台属性层
import os
import sys
import time
import cv2

# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(grandparent_dir)

from src.recognizer.image_recognizer_OCR import GameOCR
from src.tools.screen_operations import ScreenshotUtil
from loadconfig import filled_room_config, filled_room_rects, template_dir


class RoomRecognizer(GameOCR):
    def __init__(self):
        GameOCR.__init__(self)
        self.max_players = filled_room_config['max_players']
        self.window_title = filled_room_config['window_title']
        self.windowshoter = ScreenshotUtil(self.window_title)
        self.windowshot = None

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
                # print("不是Hero的回合")
                time.sleep(1)
                if time.time() - start_time > 200:  # 超过200秒
                    print(f"table_shoter，超过200秒没轮到hero")
                    return None

    # 图像匹配精度 0.9 要求高
    def image_matching(self, img_PIL, template_path, region):
        template_image = cv2.imread(template_path)
        if template_image is None:
            print(f"template: {template_path}不存在")
            return None
        result = self.windowshoter.match_template_in_screenshot(img_PIL, template_image, region, threshold=0.9)
        return result



    def is_hero_turn(self):
        file_path = os.path.join(template_dir, 'is_hero_turn.png')
        result = self.image_matching(self.windowshot, file_path, filled_room_rects['hero_turn'])
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
            result = self.image_matching(self.windowshot, file_path, filled_room_rects[f'P{i}_dealer'])
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
        return self.get_number('Last_Round_Pot')

    def get_total_pot(self):
        return self.get_number('Total_Pot')
    
    def get_publicly_cards(self):
        publicly_cards = []
        img_rank = None
        img_suit = None
        for i in range(5):
            img_rank = self.windowshot.crop(filled_room_rects[f'Board{i+1}_rank'])
            img_suit = self.windowshot.crop(filled_room_rects[f'Board{i+1}_suit'])
            poker = self.recognize_poker_card(img_rank, img_suit)
            if poker:
                publicly_cards.append(poker)
            else:
                break
        return publicly_cards
    
    def get_hero_cards(self):
        hero_cards = []
        img_rank = None
        img_suit = None
        img_rank = self.windowshot.crop(filled_room_rects['Hero_card1_rank'])
        img_suit = self.windowshot.crop(filled_room_rects['Hero_card1_suit'])
        poker = self.recognize_poker_card(img_rank, img_suit)
        if poker:
            hero_cards.append(poker)
        img_rank = self.windowshot.crop(filled_room_rects['Hero_card2_rank'])
        img_suit = self.windowshot.crop(filled_room_rects['Hero_card2_suit'])
        poker = self.recognize_poker_card(img_rank, img_suit)
        if poker:
            hero_cards.append(poker)
        return hero_cards

    def get_is_active(self, abs_position):
        active = False
        img = self.windowshot.crop(filled_room_rects[f'P{abs_position}_is_active'])
        # active  = match_check()##########
        return active

    def get_player_status(self, abs_position):
        status = None
        img = self.windowshot.crop(filled_room_rects[f'P{abs_position}_status'])
        # status = match_status()############
        return status
    
    def get_player_pot(self, abs_position):
        pot = self.get_number(f'P{abs_position}_pot')
        if pot is None: pot = 0
        return pot
    
    def get_player_funds(self, abs_position):
        funds = self.get_number(f'P{abs_position}_funds')
        if funds is None: funds = 0
        return funds

    def get_player_id(self, abs_position):
        ##########
        pass

    def get_call_value(self):
        return self.get_number('Hero_call')

    def get_bet1_value(self):
        return self.get_number('bet1')

    def get_bet2_value(self):
        return self.get_number('bet2')
    
    def get_bet3_value(self):
        return self.get_number('bet3')
    
    def get_bet4_value(self):
        return self.get_number('bet4')
    
    def get_bet5_value(self):
        return self.get_number('bet5')

    def get_coordinates(self, key):
        x = int((filled_room_rects[key][0] + filled_room_rects[key][2]) / 2)
        y = int((filled_room_rects[key][1] + filled_room_rects[key][3]) / 2)
        return (int(x), int(y))
    
    def get_player_photo_coordinates(self, abs_position):
        return self.get_coordinates(f'P{abs_position}_photo')

    # 状态监测部分
    # 状态监测部分
    # 状态监测部分
        
    def is_the_game_over(self):
        pass

    def is_hero_lost_all(self):
        pass

    def is_hero_short_funds(self):
        pass

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
        self.effective_pixel_ratio = 0.50 # 花色识别中，掩码中有效像素比例


        # 定义四种花色的HSV颜色范围
        self.pocker_color_ranges = {
            'c': ([36, 25, 25], [86, 255,255]),  # 绿色 club
            'h': ([170, 100, 50], [180, 255, 255]),  # 红色 heart
            's': ([0, 0, 0], [180, 255, 30]),     # 黑色 spade
            'd': ([94, 80, 2], [126, 255, 255]),  # 蓝色 diamond
        }


        # 定义状态的HSV颜色范围
        self.status_color_ranges = {
            'b': ([36, 25, 25], [86, 255,255]),  # 绿色 bet
            'r': ([0, 150, 50], [10, 255, 255]),  # 红色 raise
            'x': ([0, 0, 0], [180, 255, 30]),     # 黑色 check
            'c': ([94, 80, 2], [126, 255, 255]),  # 蓝色 call
            'f': ([94, 80, 2], [126, 255, 255]),  # 蓝色 fold
        }

    def windowshot_input(self, img):
        self.windowshot = img











