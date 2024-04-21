

    # handslevel
        # draw
        # TPTK, TwoPair, Set, Straight, Flush, FullHouse, Quads, StraightFlush, RoyalFlush
        # TPGK

    # outs计算
    # equity
    # EV
    # # BO VO
def postflop_strategy(t, h, p):

    # 1. 计算当前手牌的outs
    outs = Outs_Calculator(t, h).calc_outs()
    # 2. 计算当前手牌的equity
    equity = Equity(t, h).calc_equity()
    # 3. 计算当前手牌的EV
    EV = Equity(t, h).calc_EV()
    # 4. 计算当前手牌的最大投资额
    max_invest = Equity(t, h).calc_max_invest()
    # 5. 根据当前手牌的outs，equity，EV，max_invest，以及策略p，制定决策
    # 6. 返回决策
    return decision

# 调整因子：outs数量，是否有位置，是否有下注，是否有跟注，是否后位加注，底池大小，
# 分计算方案和查表方案
# 结合计算方案和查表方案

# 在池塘里 preflop多利用范围因素，flop简单利用范围因素，turn和river多利用牌面和行动线因素 

### todo 牌面分类，牌力计算（value级别，bluff级别）