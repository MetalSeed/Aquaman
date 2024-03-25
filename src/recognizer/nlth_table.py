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
    def __init__(self, abs_position):
        self.abs_position = abs_position  # 玩家座位号
        self.positon = None  # 玩家相对庄家0的位置    

        self.have_cards = False  # 是否有手牌   
        self.pot = None # 玩家当前回合的赌注
        self.funds = None  # 玩家堆栈大小        
        self.decision = None  # 玩家决定：all-in，check, call, bet, raise, fold, unknow等

        self.join_hands = False  # 是否加入了游戏
        self.active = 0  # 是否仍在游戏中 ############ 替换hands中的quit_game
        
        self.action_clip = {}
        
        self.cards = []  # 玩家的私有牌
        self.id = None  # 玩家ID

        # strategy部分
        self.position_advantage = None  # 位置优势 IP OOP
        self.range_advantage = None  # 范围优势
        self.OD_role = None # offensive deffensive
        self.action_tpye = None  # donk, cbet-flop, cbet-turn, cbet-river
        self.type_dict = None  # 玩家类型字典

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
        self.players = [Player(abs_position=i) for i in range(self.max_players)]  # 初始化max_players个玩家位置        
        
        # hero power数据
        self.bet1_power = None
        self.bet2_power = None
        self.bet3_power = None
        self.bet4_power = None
        self.bet5_power = None

        # hero button数据
        self.call_value = None
        self.bet1_value = None
        self.bet2_value = None
        self.bet3_value = None
        self.bet4_value = None
        self.bet5_value = None

    def clear(self):
        # publicly数据
        self.total_pot = None  # 总赌池大小
        self.last_round_pot = None  # 上一轮的赌池大小
        self.public_cards = None  # 公共牌
        self.dealer_abs_position = None  # 庄家位置
        # 玩家数据
        self.players = [Player(abs_position=i) for i in range(self.max_players)]  # 初始化max_players个玩家位置        
                

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

    def update_hero_bet_power(self):
        self.bet1_power = filled_room_config['bet1_power']
        self.bet2_power = filled_room_config['bet2_power']
        self.bet3_power = filled_room_config['bet3_power']
        self.bet4_power = filled_room_config['bet4_power']
        self.bet5_power = filled_room_config['bet5_power']

    def update_hero_button_value(self):
        # 直接获取call_value，因为它可能有特殊的获取方式
        self.call_value = self.prr.get_call_value()
        
        # 使用循环来更新bet值
        for i in range(1, 6):  # 生成1到5的数字
            bet_value = getattr(self.prr, f'get_betX_value')(i)
            setattr(self, f'bet{i}_value', bet_value)


    def update_players_data(self):
        for i in range(self.max_players):
            self.players[i].have_cards = self.prr.get_have_cards(i)
            self.players[i].pot = self.prr.get_player_pot(i)
            self.players[i].funds = self.prr.get_player_funds(i)
            self.players[i].decision = self.prr.get_player_decision(i)

            # jonin_hands, 'Fold'的识别准确度有待提升
            if self.players[i].have_cards is False and self.players[i].decision != 'Fold':
                self.players[i].join_hands = False
            else:
                self.players[i].join_hands = True
            
            # active
            if self.players[i].have_cards is False:
                self.players[i].active = 0
            else:
                self.players[i].active = 1
            
            # 更新hero信息
            if i == 0:
                self.players[i].join_hands = True
                self.players[i].have_cards = True
                self.players[i].active = 1
                self.players[i].decision = 'TBD'  # 'TBD'表示to be determined          
                self.players[i].cards = self.prr.get_hero_cards()
            
            # 更新成0，否则后面与None计算会出错
            if self.players[i].join_hands is True and self.players[i].pot is None:
                self.players[i].pot = 0             
            

    # 相对位置是按座位号从小到大的顺序，从庄家开始计算，庄家是0。计算前中后位，要按照total_players做离散
    def updata_players_positon(self):
        for i in range(self.max_players):
            self.players[i].position = (self.players[i].abs_position - self.dealer_abs_position + self.max_players) % self.max_players


    # 最好通过vbox的adb实现
    def undate_platyers_id(self):
        for i in range(self.max_players):
            self.players[i].id = self.prr.get_player_id(i)

    def update_table_info(self):
        self.updata_publicly_data()
        self.update_players_data()
        self.updata_players_positon()
        self.update_hero_bet_power()  
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
                        "pot": player.pot, 
                        "funds": player.funds, 
                        "decision": player.decision, 
                        
                        "join_hands": player.join_hands,
                        "active": player.active,
                        
                        "cards": player.cards,
                           'id': player.id
                            } for player in self.players],
            #hero button数据
            "call_value": self.call_value,
            "bet1_power": self.bet1_power,
            "bet2_power": self.bet2_power,
            "bet3_power": self.bet3_power,
            "bet4_power": self.bet4_power,
            "bet5_power": self.bet5_power,
        }
        
    def print_table_dict(self):
        table_dict = self.get_table_dict()
        for key, value in table_dict.items():
            if key == 'players':
                for player in value:
                    player_info = ', '.join(f"{player_key}: {player_value}" for player_key, player_value in player.items())
                    print(player_info)
            else:
                print(f"{key}: {value}")