# from stream
# from 各种谱

# 各种平台
from Aquaman.src.recognizer.nlth_table import Player, Table

actionclip = {
    'position': 1,
    'action': 'bet',
    'amount': 100,
    'size': 0.35,
    'funds': 100,
    'action_type': 'bet' # bet, 2bet, 3bet, check, cbet, donk, fold, call, all-in
}

class PlayerV2(Player):
    def __init__(self, abs_position):
        super().__init__(abs_position)

        self.position = None  # 玩家相对BTN位置
        self.actionclip = None

        self.position_advantage = None  # 位置优势 IP OOP
        self.range_advantage = None  # 范围优势
        self.OD_role = None # offensive deffensive

        self.player_type = None

class Round(Table):
    def __init__(self):
        self.clear() # 清空table属性
        self.playersV2 = [PlayerV2(abs_position=i) for i in range(9)]  # 初始化9个玩家
        
        # round数据
        self.active_players = None # 当前回合仍在游戏中的玩家数
        self.stage = None  # 当前游戏阶段：preflop, flop, turn, river  
    
    def tabledict2round(self, table_dict):
        # room data
        self.platform = table_dict['platform']
        self.max_players = table_dict['max_players']
        self.big_blind = table_dict['big_blind']
        self.small_blind = table_dict['small_blind']

        # publicly data
        self.total_pot = table_dict['total_pot']
        self.last_round_pot = table_dict['last_round_pot']
        self.publicly_cards = table_dict['publicly_cards']
        self.dealer_abs_position = table_dict['dealer_abs_position']

        for i, player in enumerate(table_dict['players']):
            self.playersV2[i].abs_position = player['abs_position']
            self.playersV2[i].is_active = player['is_active']
            self.playersV2[i].status = player['status']
            self.playersV2[i].pot = player['pot']
            self.playersV2[i].funds = player['funds']
            self.playersV2[i].cards = player['cards']
            # self.playersV2[i].id = player['id']
        
        # hero button数据
        self.call_value = table_dict['call_value']
        self.bet1_value = table_dict['bet1_value']
        self.bet2_value = table_dict['bet2_value']
        self.bet3_value = table_dict['bet3_value']
        self.bet4_value = table_dict['bet4_value']
        self.bet5_value = table_dict['bet5_value']


    def roundtext2round(self, text):
        round = Round()
        # Update round data from text
        return round

class Hands():
    def __init__(self):
        # hands数据
        self.new_hands_flag = True  # 是否有新的手牌
        self.total_players = None # 玩家总数
        self.rounds_list = []  # 所有round的列表
        self.action_list = []
    
    def cal_stage(self, round):
        if len(round.publicly_cards) == 0:
            round.stage = 'preflop'
        elif len(round.publicly_cards) == 3:
            round.stage = 'flop'
        elif len(round.publicly_cards) == 4:
            round.stage = 'turn'
        elif len(round.publicly_cards) == 5:
            round.stage = 'river'
        else:
            round.stage = None
            print(f'Stage calculation failed, cards num:{len(round.publicly_cards)}')
    
    def cal_position(self, round):
        # 计算玩家相对BTN位置
        pass
    

    def make_up_round_data(self, round):
        if self.new_hands_flag:
            # players
                # positon
                # position_advantage
                # range_advantage
            # round data
            round.active_players = sum(player.is_active for player in round.playersV2)
            pass
        else:
            # copy position
            # copy position_advantage
            # copy range_advantage
            # OD_role
            pass
        round.stage = self.cal_stage(round)
        # actionclip

    def make_up_last_round(self, round):
        # make up rounddata
        pass
    def make_up_action_list(self, round):
        # make up action_list
        pass


    def add_round(self, round):
        self.new_hands_flag = self.check_new_hands()

        if self.new_hands_flag:
            self.__init__()
            # cal total_players
            if self.total_players is None and round.stage == 'preflop':
                self.total_players = sum(1 for player in round.playersV2 if player.funds != 0 or player.pot != 0)
            # add action_list
        else:
            if self.datacheck():
                self.make_up_last_round(round)
                self.make_up_action_list(round)
                self.rounds_list.append(round)
                # add action_list
                return True
            else:
                print('Data check failed')
                return False
        self.new_hands_flag = False
    
    def check_new_hands(self):
        flag = False
        ###
        return flag

    def datacheck(self):
        check_flag = True
        # 检查数据是否完整
        return check_flag
        
class HandsConverter():
    def __init__(self):
        self.hands = Hands()
        self.round = Round()

    def hhimg2roundtextlist(self, img):
        # 从牌谱图片中解析出round text列表
        pass

    def hhtext2roundtextlist(self, text):
        # 从手牌历史文本中解析出round text列表
        pass

    def make_hands(self, hhtext):
        round_text_list = self.hhtext2roundtextlist(hhtext)
        for round_text in round_text_list:
            round = self.round.roundtext2round(round_text)
            self.hands.add_round(round)