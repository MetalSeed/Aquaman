
#
# 根据特定平台的 table_setup, 用scraper抠图，用image_recognizer识别 组装成table信息，数据交给hands_converter

# 1. 牌桌信息识别（hands,boards,delaer,round,pots,chips）
# 2. 行动信息识别（check, fold, raise，buyin，join, quit）
# 3. player数量，allin，等特殊情况识别

# platform
# wpltable



# class Table:

# 平台特定的table信息识别
# # Functions to recognize the different items on the table, based on the scraper

from screen_operations import ScreenshotUtil
from src.recognizer.image_recognizer_OCR import WePokerOCR
from src.recognizer.platform_recognizer import ScreenScraper

# 读取房间配置
# 从配置文件读取平台特定的配置信息
def get_room_config():
    config_dict = {
        'window_title': '雷电模拟器-1',
        'platform': 'wpk',
        'max_players': 8,
        'big_blind': 20,
        'small_blind': 10,
    }
    return config_dict

# 定义玩家数据结构
class Player:
    def __init__(self, abs_position, position = None, is_active=False, status='sitting', pot=0, funds=0, cards=[], id=None):
        self.abs_position = abs_position  # 玩家座位号

        self.position = position  # 玩家相对BTN位置
        self.is_active = is_active  # 是否仍在当前回合中
        
        self.status = status  # 玩家状态：sitting, all-in，check, call, bet, raise, fold等
        self.pot = pot # 玩家当前回合的赌注
        self.funds = funds  # 玩家堆栈大小

        self.id = id  # 玩家ID
        self.cards = cards  # 玩家的私有牌
        

# 定义牌桌数据结构
class Table:
    def __init__(self):
        room_config = get_room_config() # 从配置文件读取平台特定的配置信息
        # room data：窗口，平台，房间，盲注
        self.window_title = room_config['window_title'] # 窗口标题
        self.platform = room_config['platform'] # 平台
        self.max_players = room_config['max_players'] # 几人桌
        self.big_blind = room_config['big_blind'] # 大盲注大小
        self.small_blind = room_config['small_blind'] # 小盲注大小    
        # scraper 配置   
        # self.region_dict = region_dict(self.platform, self.max_players) # dict define
        # self.icon_path = icon_dir(self.platform, self.max_players) # path define

        # hands数据        
        self.total_players = None # 玩家总数
        self.dealer_position = None  # 庄家位置

        # 阶段数据
        self.community_cards = None  # 公共牌
        self.stage = 'preflop'  # 当前游戏阶段：preflop, flop, turn, river

        # 回合数据
        self.active_players = None # 当前回合仍在游戏中的玩家数
        self.total_pot = None  # 总赌池大小
        self.last_round_pot = None  # 上一轮的赌池大小
        
        #玩家数据
        self.players = [Player(abs_position=i) for i in range(9)]  # 初始化9个玩家位置

        #hero button数据
        self.call_value = None
        self.raise1_value = None
        self.raise2_value = None
        self.raise3_value = None
        self.raise4_value = None
        self.raise5_value = None

    def update_from_screenshot(self, screenshot):
        """
        根据游戏截图更新桌面信息。在实际应用中，需要图像识别技术提取信息。
        if new_hand:
            # 更新hands数        
        更新回合数据
        更新玩家数据
        """
        new_hand = self.is_it_new_hand(screenshot)
 
        # 更新hands数据
        if new_hand:
            # Update total playersß
            self.total_players = self.get_total_players(screenshot)
            # Update dealer position
            self.dealer_position = self.get_dealer_position(screenshot)
        
        # 更新stage数据
        self.community_cards = self.get_table_cards(screenshot)
        self.stage = self.get_stage(screenshot)


        # 更新回合数据
        # Update active players
        self.active_players = self.get_alive_players(screenshot)
        # Update total pot and last round pot
        self.total_pot, self.last_round_pot = self.get_pots(screenshot)

        #更新碗口数据
        self.players = self.get_players_info(screenshot)

        # Update hero buton info
        self.call_value, self.raise1_value, self.raise2_value, self.raise3_value, self.raise4_value, self.raise5_value = self.get_hero_info(screenshot)

        pass  # 实际实现需要根据游戏截图来填充属性

    # 打包成round_dict发送给hands_converter
    # hands_converter负责把round_dict parse成标准的hands信息
    def get_round_info(self):
        """
        将当前轮的信息打包成字典。
        """
        return {
            #房间数据
            "platform": self.platform,
            "max_players": self.max_players,
            "big_blind": self.big_blind,
            "small_blind": self.small_blind,
            #hands数据
            "total_players": self.total_players,
            "dealer_position": self.dealer_position,
            #阶段数据
            "stage": self.stage,
            "community_cards": self.community_cards,
            "active_players": self.active_players,
            "total_pot": self.total_pot,
            "last_round_pot": self.last_round_pot,
            #玩家数据
            "players": [{ "abs_position": player.abs_position, "position": player.position, "is_active": player.is_active, 
                          "status": player.status, "pot": player.pot, "funds": player.funds, "cards": player.cards, "id": player.id } for player in self.players],
            #hero button数据
            "call_value": self.call_value,
            "raise1_value": self.raise1_value,
            "raise2_value": self.raise2_value,
            "raise3_value": self.raise3_value,
            "raise4_value": self.raise4_value,
            "raise5_value": self.raise5_value,
        }
    
    # 判断是不是新一手
    def is_it_new_hand(screenshot):
        """
        This function should determine if a new hand has started based on the screenshot.
        The actual implementation will depend on the specifics of the game and the information available in the screenshot.
        """
        # Add your image recognition code here to determine if a new hand has started
        pass

    # Update total players
    def get_total_players(self, screenshot):
        # region = self.region_dict['total_players']
        """
        根据游戏截图识别总玩家数。
        """
        # 在这里添加识别总玩家数的代码
        pass

    def get_alive_players(self, screenshot):
        """
        根据游戏截图识别仍在游戏中的玩家数。
        """
        # 在这里添加识别仍在游戏中的玩家数的代码
        pass

    def get_dealer_position(self, screenshot):
        """
        根据游戏截图识别庄家位置。
        """
        # 在这里添加识别庄家位置的代码
        pass

    def get_pots(self, screenshot):
        """
        根据游戏截图识别总赌池大小和上一轮的赌池大小。
        """
        # 在这里添加识别赌池大小的代码
        pass

    def get_table_cards(self, screenshot):
        """
        根据游戏截图识别公共牌。
        """
        # 在这里添加识别公共牌的代码
        pass

    def get_players_info(self, screenshot):
        """
        根据游戏截图识别玩家信息，包括玩家动作，赌注，资金，位置等。
        """
        # 在这里添加识别玩家信息的代码
        pass

    def get_hero_info(self, screenshot):
        """
        根据游戏截图识别英雄信息，包括英雄的牌，赌注，资金，位置，叫牌值，加注值等。
        """
        # 在这里添加识别英雄信息的代码
        # get hero cards
        # get call value
        # get raise1 value
        # get raise2 value
        # get raise3 value
        # get raise4 value
        # get raise5 value
        pass

    
  
# 示例使用
table = Table()
# 假设有一个函数capture_screenshot()用于捕获当前屏幕截图
# screenshot = capture_screenshot()
# table.update_from_screenshot(screenshot)
round_info = table.get_round_info()

print(round_info)  # 打印当前轮的信息



# 基础识别器定义在basic_recognizer.py中(与平台无关)
# platform_recognizer.py定义不同平台的识别器（平台相关）
# recognize_table.py 定义 recognizer = wpk_recognizer()  # 制定识别器和数据路径
# 定义不同平台的识别和路径