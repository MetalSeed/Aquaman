# 通用table信息识别
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

from src.recognizer.platform_recognizer import filled_room_config, wpkRR

# from config import load_config

# 定义玩家数据结构
class Player:
    def __init__(self, abs_position, position = None, is_active=False, status='empt', pot=0, funds=0, cards=[], id=None):
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
        self.prr = eval(f"{filled_room_config['platform']}RR()") # platform room recognizer
        # room data
        self.max_players = None
        self.big_blind = None # 大盲注大小
        self.small_blind = None# 小盲注大小    
        self.update_room_data()

        # publicly数据
        self.total_pot = None  # 总赌池大小
        self.last_round_pot = None  # 上一轮的赌池大小
        self.dealer_abs_position = None  # 庄家位置
        self.publicly_cards = None  # 公共牌
        
        # 玩家数据
        self.players = [Player(abs_position=i) for i in range(self.max_players)]  # 初始化9个玩家位置        
        
        # hero button数据
        self.call_value = None
        self.bet1_value = None
        self.bet2_value = None
        self.bet3_value = None
        self.bet4_value = None
        self.bet5_value = None



    def update_room_data(self):
        self.max_players = filled_room_config['max_players']
        self.big_blind = filled_room_config['big_blind']
        self.small_blind = filled_room_config['small_blind']
    
    def updata_publicly_data(self):
        self.total_pot = self.prr.get_total_pot()
        self.last_round_pot = self.prr.get_last_round_pot()
        self.dealer_abs_position = self.prr.get_dealer_abs_position()
        self.publicly_cards = self.prr.get_publicly_cards()

    def updata_hero_button_data(self):
        self.call_value = self.prr.get_call_value()
        self.bet1_value = self.prr.get_bet1_value()
        self.bet2_value = self.prr.get_bet2_value()
        self.bet3_value = self.prr.get_bet3_value()
        self.bet4_value = self.prr.get_bet4_value()
        self.bet5_value = self.prr.get_bet5_value()


    def update_players_data(self):
        for i in range(self.max_players):
            if i == 0:
                self.players[i].is_active = True
                self.players[i].status = 'tbd'  # 'tbd'表示to be determined          
                self.players[i].cards = self.prr.get_hero_cards()
            else:
                self.players[i].is_active = self.prr.get_is_active(i)
                self.players[i].status = self.prr.get_player_status(i)
                # self.players[i].id = self.prr.get_player_id(i)
            self.players[i].pot = self.prr.get_player_pot(i)
            self.players[i].funds = self.prr.get_player_funds(i)

    def update_table_info(self):
        self.updata_publicly_data()
        self.update_players_data()
        self.updata_hero_button_data()  

    # 打包成table_dict发送给hands_converter
    # hands_converter负责把table_dict parse成标准的hands信息
    def get_table_info(self):
        # 将当前桌面信息打包成字典。
        return {
            #房间数据
            "max_players": self.max_players,
            "big_blind": self.big_blind,
            "small_blind": self.small_blind,

            #publicly数据
            "total_pot": self.total_pot,
            "last_round_pot": self.last_round_pot,
            "publicly_cards": self.publicly_cards,
            "dealer_abs_position": self.dealer_abs_position,
            
            #玩家数据
            "players": [{ "abs_position": player.abs_position, "is_active": player.is_active, 
                          "status": player.status, "pot": player.pot, "funds": player.funds, "cards": player.cards } for player in self.players],
            #hero button数据
            "call_value": self.call_value,
            "bet1_value": self.bet1_value,
            "bet2_value": self.bet2_value,
            "bet3_value": self.bet3_value,
            "bet4_value": self.bet4_value,
            "bet5_value": self.bet5_value,
        }
    



#增加到round信息里
        # self.total_players = None # 玩家总数
        # self.active_players = None # 当前回合仍在游戏中的玩家数
        # self.stage = None  # 当前游戏阶段：preflop, flop, turn, river