import logging
import numpy as np
from enum import Enum
import random


log = logging.getLogger(__name__)
# winPro = Equity

class DecisionTypes(Enum):
    i_am_back, fold, check, call, bet1, bet2, bet3, bet4, bet5, bet_bluff, call_deception, check_deception = \
    ['Imback', 'F', 'X', 'C', 'B1', 'B2', 'B3', 'B4', 'B5', 'Bet Bluff', 'Call Deception', 'Check Deception']

class Positions(Enum):
    SB, BB, UTG, EP1, EP2, MP1, MP2, CO, BTN = [1, 2, 3, 4, 5, 6, 7, 8, 0]

class Stages(Enum):
    preflop, flop, turn, river = ['preflop', 'flop', 'turn', 'river']

class PotTypes(Enum):
    single_raise, multi_raise, single_call, multi_call, raise_call, call_raise, call_call = \
    ['single raise', 'multi raise', 'single call', 'multi call', 'raise call', 'call raise', 'call call']


class BasicAnalysis:
    # 位置 事件 范围，EV 偏移 赢啥 换思 阻断， 频率 偏差
    # preflop 计算
    
    # 获得手牌缩写, ABs, ABo, AA 
    def get_cards_abbreviation(self, input_cards, add_o_to_pairs=False):
        card_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
        card1 = input_cards[0][0]
        card2 = input_cards[1][0]
        suited_str = 's' if input_cards[0][1] == input_cards[1][1] else 'o'
        if card1[0] == card2[0]:
            if add_o_to_pairs: suited_str = "o"
            else: suited_str = ''
        if card_values[card1] < card_values[card2]: card1, card2 = card2, card1
        return card1 + card2 + suited_str


class DecisionBase(BasicAnalysis):
    # Contains routines that make the actual decisions to play: the main function is make_decision
    def calc_bet_EV(self, E, P, S, c, table): # Equity, Pot, Steak, Config, Table
        # param c: 配置参数，可能影响计算
        n = 1 if table.isHeadsUp else 2 # 单挑地池n=1, 否则n=2
        f = max(0, 1 - min(S / P, 1)) * c * n # 调整因子，下注大，跟注就会小少，下注小，跟注可能性大。C是群体偏移和玩家偏移
        EV = E * (P + f) - (1 - E) * S
        return EV
    
    def calc_call_EV(self, E, P, S): # Equity, Pot, Steak
        EV = (E * (P - S + S)) - ((1 - E) * S)
        return EV

    def calc_EV_call_limit(self, E, P): # Equity, Pot
        MaxCall = 10
        CallValues = np.arange(0.01, MaxCall, 0.01)
        EV = [self.calc_call_EV(E, P, S) for S in CallValues]
        BestEquity = min(EV, key=lambda x: abs(x - 0)) #找到最接近0的EV
        return CallValues[EV.index(BestEquity)] #返回对应的下注金额

    def calc_bet_limit(self, E, P, c, t, logger): # Equity, Pot, Config, Table
        # return: 最大下注金额
        Step = 0.01
        MaxCall = 1000
        rng = int(np.round((1 * Step + MaxCall) / Step))
        EV = [self.calc_bet_EV(E, P, S * Step, c, t) for S in range(rng)]
        X = range(rng)  # pylint: disable=unused-variable

        # plt.plot(X[1:200],EV[1:200])
        # plt.show()

        BestEquity = max(EV)
        logger.debug("Experimental maximum EV for betting: " + str(BestEquity))
        _ = EV.index(BestEquity)
        self.maxEvBetSize = np.round(EV.index(BestEquity) * Step, 2)
        return self.maxEvBetSize

    def calc_max_invest(self, equity, pw, bigBlindMultiplier):
        """
        计算最大投资额
        :param equity: 玩家的胜率
        :param pw: 权重
        :param bigBlindMultiplier: 大盲注倍数
        :return: 计算得到的最大投资额
        """        
        return np.round((equity ** pw) * bigBlindMultiplier, 2)


class Decison(DecisionBase):
    def __init__(self, hands):
        # 游戏阶段
        self.stage = hands.rounds_list[-1].stage

        # 玩家情况
        self.total_players = hands.total_players
        self.quit_players = len(set(hands.quit_list)) 
        self.active_players = sum(1 for player in hands.rounds_list[-1].players if player.active == 1)
        self.active_players_behind = sum(1 for action_clip in hands.actions_lists[self.stage] if action_clip['action'] == 'TBD') - 1
        self.active_players_front = self.total_players - self.quit_players - self.active_players_behind - 1

        # 位置情况
        self.inposition = False
        
        # 底池情况
        self.single_raise_pot = False

        # 范围情况
        self.preflop_hero_ranges = None
        
        # hero信息
        self.hero_position_name = hands.rounds_list[-1].players[0].position_name
        self.hero_cards = hands.rounds_list[-1].players[0].cards
        self.hero_cards_abbreviation = self.get_cards_abbreviation(self.hero_cards)
    



    def calc_equity(self):
        pass

    def calc_EV(self):
        pass

    def make_decision(self, hands, strategy, gamelogger):
        stage = hands.rounds_list[-1].stage
        if stage == Stages.preflop.value:
            self.preflop_table_analyser(hands, strategy)
        elif stage == Stages.flop.value:
            pass
        elif stage == Stages.turn.value:
            pass
        elif stage == Stages.river.value:
            pass



