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

from src.recognizer.nlth_platform import filled_room_config, wpkRR


# 定义玩家数据结构
class Player:
    def __init__(self, abs_position, have_cards=False, status=None, pot=None, funds=None, cards=[], id=None, quit_flag = False):
        self.abs_position = abs_position  # 玩家座位号
        self.have_cards = have_cards  # 是否仍在当前回合中   
        
        self.positon = None  # 玩家相对庄家的位置    
        self.status = status  # 玩家状态：sitting, all-in，check, call, bet, raise, fold等
        self.pot = pot # 玩家当前回合的赌注
        self.funds = funds  # 玩家堆栈大小
        self.action_clip = {}

        self.cards = cards  # 玩家的私有牌
        self.id = id  # 玩家ID

        # strategy部分
        self.position_advantage = None  # 位置优势 IP OOP
        self.range_advantage = None  # 范围优势
        self.OD_role = None # offensive deffensive
        self.action_tpye = None  # donk, cbet-flop, cbet-turn, cbet-river
        self.player_type = None

# 定义牌桌数据结构
class Table:
    def __init__(self):
        self.prr = eval(f"{filled_room_config['platform']}RR()") # platform room recognizer
        # room数据
        self.platform = None
        self.max_players = None
        self.big_blind = None
        self.small_blind = None  

        self.update_room_data()

        # publicly数据
        self.total_pot = None  # 总赌池大小
        self.last_round_pot = None  # 上一轮的赌池大小
        self.public_cards = None  # 公共牌
        self.dealer_abs_position = None  # 庄家位置
        
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
        self.platform = filled_room_config['platform']
        self.max_players = filled_room_config['max_players']
        self.big_blind = filled_room_config['big_blind']
        self.small_blind = filled_room_config['small_blind']
    
    def updata_publicly_data(self):
        self.pot_total = self.prr.get_total_pot()
        self.pot_last_round = self.prr.get_last_round_pot()
        self.dealer_abs_position = self.prr.get_dealer_abs_position()
        self.public_cards = self.prr.get_public_cards()

    def update_hero_button_power(self):
        self.bet1_value = filled_room_config['bet1_power']
        self.bet2_value = filled_room_config['bet2_power']
        self.bet3_value = filled_room_config['bet3_power']
        self.bet4_value = filled_room_config['bet4_power']
        self.bet5_value = filled_room_config['bet5_power']

    def update_hero_button_data(self):
        self.call_value = self.prr.get_call_value()
        self.bet1_value = self.prr.get_bet1_value()
        self.bet2_value = self.prr.get_bet2_value()
        self.bet3_value = self.prr.get_bet3_value()
        self.bet4_value = self.prr.get_bet4_value()
        self.bet5_value = self.prr.get_bet5_value()


    def update_players_data(self):
        for i in range(self.max_players):
            if i == 0:
                self.players[i].have_cards = True
                self.players[i].status = 'tbd'  # 'tbd'表示to be determined          
                self.players[i].cards = self.prr.get_hero_cards()
            else:
                self.players[i].have_cards = self.prr.get_have_cards(i)
                self.players[i].status = self.prr.get_player_status(i)
            self.players[i].pot = self.prr.get_player_pot(i)
            self.players[i].funds = self.prr.get_player_funds(i)

    # 相对位置是按座位号从小到大的顺序，从庄家开始计算，庄家是0。计算前中后位，要按照total_players做离散
    def updata_players_positon(self):
        for i in range(self.max_players):
            self.players[i].position = (self.players[i].abs_position - self.dealer_abs_position + self.max_players) % self.max_players


    def undate_platyers_id(self):
        for i in range(self.max_players):
            self.players[i].id = self.prr.get_player_id(i)

    def update_table_info(self):
        self.updata_publicly_data()
        self.update_players_data()
        # self.update_hero_button_data()  
        self.update_hero_button_power()  
        self.updata_players_positon()
        # self.undate_platyers_id()

    # 打包成dict,交给converter转换成round
    def get_table_dict(self):
        # 将当前桌面信息打包成字典。
        return {
            #房间数据
            "platform": self.platform,
            "max_players": self.max_players,
            "big_blind": self.big_blind,
            "small_blind": self.small_blind,

            #publicly数据
            "pot_total": self.pot_total,
            "pot_last_round": self.pot_last_round,
            "public_cards": self.public_cards,
            "dealer_abs_position": self.dealer_abs_position,
            
            #玩家数据
            "players": [{ 
                        "abs_position": player.abs_position,
                        "position": player.position,
                        "have_cards": player.have_cards, 
                        "status": player.status, 
                        "pot": player.pot, 
                        "funds": player.funds, 
                        "cards": player.cards,
                        #    'id': player.id
                            } for player in self.players],
            #hero button数据
            "call_value": self.call_value,
            "bet1_value": self.bet1_value,
            "bet2_value": self.bet2_value,
            "bet3_value": self.bet3_value,
            "bet4_value": self.bet4_value,
            "bet5_value": self.bet5_value,
        }
    
    def room_check(self):
        # 短码，输光，等情况
        # 检查各种异常情况
        # 少于4人，quit game
        pass