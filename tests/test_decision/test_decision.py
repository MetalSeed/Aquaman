
import numpy as np


class DecisionBase:
    # Contains routines that make the actual decisions to play: the main function is make_decision
    def calc_bet_EV(self, E, P, S, c, table):
        """
        计算下注的期望值(EV)
        :param E: 玩家手牌的胜率
        :param P: 当前底池的大小
        :param S: 需要下注的金额
        :param c: 配置参数，可能影响计算
        :param table: 游戏桌面信息
        :return: 下注的期望值
        """
        n = 1 if table.isHeadsUp else 2 # 单挑地池n=1, 否则n=2
        f = max(0, 1 - min(S / P, 1)) * c * n # 调整因子，下注大，跟注就会小少，下注小，跟注可能性大。C是群体偏移和玩家偏移
        EV = E * (P + f) - (1 - E) * S
        return EV

    def calc_call_EV(self, E, P, S):
        """
        计算跟注的期望值(EV)
        :param E: 玩家手牌的胜率
        :param P: 当前底池的大小
        :param S: 需要跟注的金额
        :return: 跟注的期望值
        """
        EV = (E * (P - S + S)) - ((1 - E) * S)
        return EV

    def calc_EV_call_limit(self, E, P):
        """
        计算零期望值跟注大小
        :param E: 玩家手牌的胜率
        :param P: 当前底池的大小
        :return: 零期望值时的跟注金额
        """        
        MaxCall = 10
        CallValues = np.arange(0.01, MaxCall, 0.01)
        EV = [self.calc_call_EV(E, P, S) for S in CallValues]
        BestEquity = min(EV, key=lambda x: abs(x - 0))
        # _ = EV.index(BestEquity)
        # self.zeroEvCallSize = np.round(EV.index(BestEquity), 2)
        return CallValues[EV.index(BestEquity)]

    def calc_bet_limit(self, E, P, c, t, logger):
        """
        计算下注限制
        :param E: 玩家手牌的胜率
        :param P: 当前底池的大小
        :param c: 配置参数
        :param t: 游戏桌面信息
        :param logger: 日志记录器
        :return: 最大下注金额
        """        
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

D = DecisionBase()

EV = D.calc_call_EV(0.3, 100, 45)
EV = D.calc_EV_call_limit(0.3, 15)
print(abs(-13))
print(EV)

cards = ["Tc","Ts"]
print(D.get_cards_abbreviation(cards))

