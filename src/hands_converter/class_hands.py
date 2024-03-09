# from stream
# from 各种谱

# 各种平台
from Aquaman.src.recognizer.nlth_table import Player

action = {
    'position': 1,
    'action': 'bet',
    'amount': 100,
    'size': 0.35
}

class Player2(Player):
    def __init__(self, abs_position, position = None, is_active=False, status='empt', pot=0, funds=0, cards=[], id=None):
        super().__init__(abs_position, position, is_active, status, pot, funds, cards, id)

        self.action = None
        self.player_type = None

class Round():
    def __init__(self):
        # room 数据
        self.max_players = None
        self.big_blind = None # 大盲注大小
        self.small_blind = None# 小盲注大小    

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

        # round数据
        self.active_players = None # 当前回合仍在游戏中的玩家数
        self.stage = None  # 当前游戏阶段：preflop, flop, turn, river 

    def update_round_data(self):
        # 从table数据，计算round数据
        pass
    
    def tabledict2round(self, table_dict):
        # copy data from table_dict
        self.max_players = table_dict.get('max_players')
        self.big_blind = table_dict.get('big_blind')
        self.small_blind = table_dict.get('small_blind')

        self.total_pot = table_dict.get('total_pot')
        self.last_round_pot = table_dict.get('last_round_pot')
        self.dealer_abs_position = table_dict.get('dealer_abs_position')
        self.publicly_cards = table_dict.get('publicly_cards')
        self.players = [Player(abs_position=i) for i in range(round.max_players)]

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
        self.hands_history = []

    def hands_init(self):
        if self.hands_history is not []:
            # save hands_history
            pass
        self.new_hands_flag = True
        self.total_players = None 
        self.hands_history = []
    
    def add_round(self, round):
        self.new_hands_flag = True
        if self.new_hands_flag:
            # hands_init()
            pass
        self.new_hands_flag = True
        if self.datacheck():
            self.rounds_list.append(round)
            return True
        else:
            print('Data check failed')
            return False

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