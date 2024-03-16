# from stream
# from 各种谱

# 各种平台
from Aquaman.src.recognizer.nlth_table import Player, Table

action_clip = {
    'position': 1,
    'action': 'bet',  # Bet, Raise, Call, Check, Fold, All-in
    'funds': 100,
    'pot': 100,
}
        
class Round(Table):
    def __init__(self):
        super().__init__()
        # round数据
        self.stage = None  # 当前游戏阶段：preflop, flop, turn, river  
    
    def get_stage(self):
        if len(self.publicly_cards) == 0:
            self.stage = 'preflop'
        elif len(self.publicly_cards) == 3:
            self.stage = 'flop'
        elif len(self.publicly_cards) == 4:
            self.stage = 'turn'
        elif len(self.publicly_cards) == 5:
            self.stage = 'river'
        else:
            self.stage = None
            print(f'Stage calculation failed, cards num:{len(self.publicly_cards)}')

    def post_process_round_data(self):
        self.stage = self.get_stage()
    

    def tabledict2round(self, table_dict): # 通过ir的table字典读取round数据
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
            self.playersV2[i].position = player['position']
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
        # 数据后处理
        self.post_process_round_data()

    def roundtext2round(self, text): # 通过文本或者手牌历史读取round数据
        round = Round()
        # Update round data from text
        return round
    
    def adbtext2round(self, text): # 通过adb读取round数据
        round = Round()
        # Update round data from text
        return round

class Hands():
    
    # add_round（）, decision = make_decision(), add_hero_decision(decision)
    def __init__(self):
        # hands数据
        self.new_hands_flag = True  # 是否有新的手牌
        self.rounds_list = []  # 所有round的列表
        self.total_players = None # 玩家总数
        self.quit_list = []  # 退出玩家列表
        
        self.actions_list_preflop = []
        self.actions_list_flop = []
        self.actions_list_turn = []
        self.actions_list_river = []

        self.raiser_list_preflop = []  # 当前回合加注者列表
        self.raiser_list_flop = []
        self.raiser_list_turn = []
        self.raiser_list_river = []
    
    def add_hero_decision(self, decision): # F C X Rx Bx 
        temp_action = {'position': None, 'action': None, 'pot': 0, 'funds': 0, 'abs_position': 0}
        temp_action['abs_position'] = self.rounds_list[-1].players[0].abs_position

        if decision == 'F':
            temp_action['action'] = 'Fold'
            temp_action['pot'] = 0
            temp_action['funds'] = -1
            # 加入到actions_list没有实现
        elif decision == 'X':
            temp_action['action'] = 'Check'
            temp_action['pot'] = 0
            temp_action['funds'] = self.rounds_list[-1].players[0].funds
        elif decision == 'C':
            temp_action['action'] = 'Call'
            if self.rounds_list[-1].stage == 'preflop':
                temp_action['pot'] = self.raiser_list_preflop[-1]['pot']
                temp_action['funds'] = self.rounds_list[-1].players[0].funds - (self.raiser_list_preflop[-1]['pot'] - self.rounds_list[-1].players[0].pot)

            elif self.rounds_list[-1].stage == 'flop':
                temp_action['pot'] = self.raiser_list_flop[-1]['pot']
                temp_action['funds'] = self.rounds_list[-1].players[0].funds - (self.raiser_list_flop[-1]['pot'] - self.rounds_list[-1].players[0].pot)
            elif self.rounds_list[-1].stage == 'turn':
                temp_action['pot'] = self.raiser_list_turn[-1]['pot']
                temp_action['funds'] = self.rounds_list[-1].players[0].funds - (self.raiser_list_turn[-1]['pot'] - self.rounds_list[-1].players[0].pot)
            elif self.rounds_list[-1].stage == 'river':
                temp_action['pot'] = self.raiser_list_river[-1]['pot']
                temp_action['funds'] = self.rounds_list[-1].players[0].funds - (self.raiser_list_river[-1]['pot'] - self.rounds_list[-1].players[0].pot)
        elif decision == 'R1':
            if self.rounds_list[-1].stage == 'preflop':
                if len(self.raiser_list_preflop) == 0: # bet
                    temp_action['action'] = 'Bet1'
                    temp_action['pot'] = 111# total pot * 0.3
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                else: # raise
                    temp_action['action'] = 'Raise1'
                    temp_action['pot'] = 111# total pot * 0.3
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
            elif self.rounds_list[-1].stage == 'flop':
                if len(self.raiser_list_flop) == 0:
                    temp_action['action'] = 'Bet1'
                    temp_action['pot'] = 111# total pot * 0.3
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                else:
                    temp_action['action'] = 'Raise1'
                    temp_action['pot'] = 111
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
            elif self.rounds_list[-1].stage == 'turn':
                if len(self.raiser_list_turn) == 0:
                    temp_action['action'] = 'Bet1'
                    temp_action['pot'] = 111
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                else:
                    temp_action['action'] = 'Raise1'
                    temp_action['pot'] = 111
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
            elif self.rounds_list[-1].stage == 'river':
                if len(self.raiser_list_river) == 0:
                    temp_action['action'] = 'Bet1'
                    temp_action['pot'] = 111
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                else:
                    temp_action['action'] = 'Raise1'
                    temp_action['pot'] = 111
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)

        elif decision == 'R2':
            if self.rounds_list[-1].stage == 'preflop':
                if len(self.raiser_list_preflop) == 0:
                    temp_action['action'] = 'Bet2'
                    temp_action['pot'] = 222
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                else:
                    temp_action['action'] = 'Raise2'
                    temp_action['pot'] = 222
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
            elif self.rounds_list[-1].stage == 'flop':
                if len(self.raiser_list_flop) == 0:
                    temp_action['action'] = 'Bet2'
                    temp_action['pot'] = 222
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                else:
                    temp_action['action'] = 'Raise2'
                    temp_action['pot'] = 222
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
            elif self.rounds_list[-1].stage == 'turn':
                if len(self.raiser_list_turn) == 0:
                    temp_action['action'] = 'Bet2'
                    temp_action['pot'] = 222
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                else:
                    temp_action['action'] = 'Raise2'
                    temp_action['pot'] = 222
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
            elif self.rounds_list[-1].stage == 'river':
                if len(self.raiser_list_river) == 0:
                    temp_action['action'] = 'Bet2'
                    temp_action['pot'] = 222
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                else:
                    temp_action['action'] = 'Raise2'
                    temp_action['pot'] = 222
                    temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
            elif decision == 'R3':
                if self.rounds_list[-1].stage == 'preflop':
                    if len(self.raiser_list_preflop) == 0:
                        temp_action['action'] = 'Bet3'
                        temp_action['pot'] = 333
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                    else:
                        temp_action['action'] = 'Raise3'
                        temp_action['pot'] = 333
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
                elif self.rounds_list[-1].stage == 'flop':
                    if len(self.raiser_list_flop) == 0:
                        temp_action['action'] = 'Bet3'
                        temp_action['pot'] = 333
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                    else:
                        temp_action['action'] = 'Raise3'
                        temp_action['pot'] = 333
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
                elif self.rounds_list[-1].stage == 'turn':
                    if len(self.raiser_list_turn) == 0:
                        temp_action['action'] = 'Bet3'
                        temp_action['pot'] = 333
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                    else:
                        temp_action['action'] = 'Raise3'
                        temp_action['pot'] = 333
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
                elif self.rounds_list[-1].stage == 'river':
                    if len(self.raiser_list_river) == 0:
                        temp_action['action'] = 'Bet3'
                        temp_action['pot'] = 333
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                    else:
                        temp_action['action'] = 'Raise3'
                        temp_action['pot'] = 333
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
            elif decision == 'R4':
                if self.rounds_list[-1].stage == 'preflop':
                    if len(self.raiser_list_preflop) == 0:
                        temp_action['action'] = 'Bet4'
                        temp_action['pot'] = 444
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                    else:
                        temp_action['action'] = 'Raise4'
                        temp_action['pot'] = 444
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
                elif self.rounds_list[-1].stage == 'flop':
                    if len(self.raiser_list_flop) == 0:
                        temp_action['action'] = 'Bet4'
                        temp_action['pot'] = 444
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                    else:
                        temp_action['action'] = 'Raise4'
                        temp_action['pot'] = 444
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
                elif self.rounds_list[-1].stage == 'turn':
                    if len(self.raiser_list_turn) == 0:
                        temp_action['action'] = 'Bet4'
                        temp_action['pot'] = 444
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                    else:
                        temp_action['action'] = 'Raise4'
                        temp_action['pot'] = 444
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
                elif self.rounds_list[-1].stage == 'river':
                    if len(self.raiser_list_river) == 0:
                        temp_action['action'] = 'Bet4'
                        temp_action['pot'] = 444
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                    else:
                        temp_action['action'] = 'Raise4'
                        temp_action['pot'] = 444
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
            elif decision == 'R5':
                if self.rounds_list[-1].stage == 'preflop':
                    if len(self.raiser_list_preflop) == 0:
                        temp_action['action'] = 'Bet5'
                        temp_action['pot'] = 555
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                    else:
                        temp_action['action'] = 'Raise5'
                        temp_action['pot'] = 555
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
                elif self.rounds_list[-1].stage == 'flop':
                    if len(self.raiser_list_flop) == 0:
                        temp_action['action'] = 'Bet5'
                        temp_action['pot'] = 555
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                    else:
                        temp_action['action'] = 'Raise5'
                        temp_action['pot'] = 555
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
                elif self.rounds_list[-1].stage == 'turn':
                    if len(self.raiser_list_turn) == 0:
                        temp_action['action'] = 'Bet5'
                        temp_action['pot'] = 555
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                    else:
                        temp_action['action'] = 'Raise5'
                        temp_action['pot'] = 555
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
                elif self.rounds_list[-1].stage == 'river':
                    if len(self.raiser_list_river) == 0:
                        temp_action['action'] = 'Bet5'
                        temp_action['pot'] = 555
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - temp_action['pot']
                    else:
                        temp_action['action'] = 'Raise5'
                        temp_action['pot'] = 555
                        temp_action['funds'] = self.rounds_list[-1].players[0].funds - (temp_action['pot'] - self.rounds_list[-1].players[0].pot)
        else:
            print('Decision error hands.py 313')


    # 补全上一阶段的遗漏行动, round是要添加的round
    def make_up_actions_list(self, round): # hero to last raiser
        if self.rounds_list[-1].stage == 'preflop':
            if len(self.raiser_list_preflop) == 0: # all limp
                for i in range(len(self.actions_list_preflop)):
                    if self.actions_list_preflop[i]['action'] == 'TBD':
                        if round.players[self.actions_list_preflop[i]['abs_position']].status is 'Fold' or round.players[self.actions_list_preflop[i]['abs_position']].is_active is False:
                            self.actions_list_preflop[i]['action'] = 'Fold'
                            self.quit_list.append(self.actions_list_preflop[i]['abs_position'])
                        else:
                            self.actions_list_preflop[i]['action'] = 'Call'
                            self.actions_list_preflop[i]['pot'] = round.big_blind
                            self.actions_list_preflop[i]['funds'] = round.players[self.actions_list_preflop[i]['abs_position']].funds + round.players[self.actions_list_preflop[i]['abs_position']].pot
            else: # call or fold
                for i in range(len(self.actions_list_preflop)):
                    if self.actions_list_preflop[i]['action'] == 'TBD':
                        if round.players[self.actions_list_preflop[i]['abs_position']].status is 'Fold' or round.players[self.actions_list_preflop[i]['abs_position']].is_active is False:
                            self.actions_list_preflop[i]['action'] = 'Fold'
                            self.quit_list.append(self.actions_list_preflop[i]['abs_position'])
                        else:
                            self.actions_list_preflop[i]['action'] = 'Call'
                            self.actions_list_preflop[i]['pot'] = self.raiser_list_preflop[-1]['pot']
                            self.actions_list_preflop[i]['funds'] = round.players[self.actions_list_preflop[i]['abs_position']].funds + round.players[self.actions_list_preflop[i]['abs_position']].pot
        elif self.rounds_list[-1].stage == 'flop':
            if len(self.raiser_list_flop) == 0: # all check or fold
                for i in range(len(self.actions_list_flop)):
                    if self.actions_list_flop[i]['action'] == 'TBD':
                        if round.players[self.actions_list_flop[i]['abs_position']].status is 'Fold' or round.players[self.actions_list_flop[i]['abs_position']].is_active is False:
                            self.actions_list_flop[i]['action'] = 'Fold'
                            self.quit_list.append(self.actions_list_flop[i]['abs_position'])
                        else:
                            self.actions_list_flop[i]['action'] = 'Check'
                            self.actions_list_flop[i]['pot'] = 0
                            self.actions_list_flop[i]['funds'] = round.players[self.actions_list_flop[i]['abs_position']].funds + round.players[self.actions_list_flop[i]['abs_position']].pot
            else: # call or fold
                for i in range(len(self.actions_list_flop)):
                    if self.actions_list_flop[i]['action'] == 'TBD':
                        if round.players[self.actions_list_flop[i]['abs_position']].status is 'Fold' or round.players[self.actions_list_flop[i]['abs_position']].is_active is False:
                            self.actions_list_flop[i]['action'] = 'Fold'
                            self.quit_list.append(self.actions_list_flop[i]['abs_position'])
                        else:
                            self.actions_list_flop[i]['action'] = 'Call'
                            self.actions_list_flop[i]['pot'] = self.raiser_list_flop[-1]['pot']
                            self.actions_list_flop[i]['funds'] = round.players[self.actions_list_flop[i]['abs_position']].funds + round.players[self.actions_list_flop[i]['abs_position']].pot
        elif self.rounds_list[-1].stage == 'turn':
            if len(self.raiser_list_turn) == 0: # all check or fold
                for i in range(len(self.actions_list_turn)):
                    if self.actions_list_turn[i]['action'] == 'TBD':
                        if round.players[self.actions_list_turn[i]['abs_position']].status is 'Fold' or round.players[self.actions_list_turn[i]['abs_position']].is_active is False:
                            self.actions_list_turn[i]['action'] = 'Fold'
                            self.quit_list.append(self.actions_list_turn[i]['abs_position'])
                        else:
                            self.actions_list_turn[i]['action'] = 'Check'
                            self.actions_list_turn[i]['pot'] = 0
                            self.actions_list_turn[i]['funds'] = round.players[self.actions_list_turn[i]['abs_position']].funds + round.players[self.actions_list_turn[i]['abs_position']].pot
            else: # call or fold
                for i in range(len(self.actions_list_turn)):
                    if self.actions_list_turn[i]['action'] == 'TBD':
                        if round.players[self.actions_list_turn[i]['abs_position']].status is 'Fold' or round.players[self.actions_list_turn[i]['abs_position']].is_active is False:
                            self.actions_list_turn[i]['action'] = 'Fold'
                            self.quit_list.append(self.actions_list_turn[i]['abs_position'])
                        else:
                            self.actions_list_turn[i]['action'] = 'Call'
                            self.actions_list_turn[i]['pot'] = self.raiser_list_turn[-1]['pot']
                            self.actions_list_turn[i]['funds'] = round.players[self.actions_list_turn[i]['abs_position']].funds + round.players[self.actions_list_turn[i]['abs_position']].pot


    def add_actions_list(self, round, new_stage_flag): # 涉及对round的修改，要调整
        # 添加已经行动的人
        # 设置list起点和终点
        if new_stage_flag: # new stage
            if round.stage != 'preflop': # 'flop', 'turn', 'river'
                start_abs_postion = (round.dealer_abs_position + 1) % round.max_players # SB
                
            else: # 'preflop'
                start_abs_postion = (round.dealer_abs_position + 3) % round.max_players # UTG
        else: # repeat stage
            start_abs_postion = 1
        end_abs_postion = round.max_players

        for i in range(start_abs_postion, end_abs_postion):
            if i in self.quit_list: continue # 已经出局，跳过

            # 入座中或者空位，标记出局，跳过
            if self.round.players[i].status == 'Waitting' or self.round.players[i].status == 'Empty': 
                self.quit_list.append(i)
                continue
            
            # 如果弃牌，标记出局
            if self.round.players[i].is_active is False or self.round.players[i].status == 'Fold':
                self.quit_list.append(i)
            
            temp_action = {'position': None, 'action': None, 'pot': 0, 'funds': 0, 'abs_position': None}
            temp_action['abs_position'] = i
            temp_action['position'] = round.players[i].position
            temp_action['action'] = round.players[i].status
            temp_action['pot'] = round.players[i].pot
            temp_action['funds'] = round.players[i].funds

            # add to actions list and raiser list
            if round.stage == 'preflop':
                self.actions_list_preflop.append(temp_action)
                if temp_action['action'] == 'Bet' or temp_action['action'] == 'Raise':
                    self.raiser_list_preflop.append(temp_action)
            elif round.stage == 'flop':
                self.actions_list_flop.append(temp_action)
                if temp_action['action'] == 'Bet' or temp_action['action'] == 'Raise':
                    self.raiser_list_flop.append(temp_action)
            elif round.stage == 'turn':
                self.actions_list_turn.append(temp_action)
                if temp_action['action'] == 'Bet' or temp_action['action'] == 'Raise':
                    self.raiser_list_turn.append(temp_action)
            elif round.stage == 'river':
                self.actions_list_river.append(temp_action)
                if temp_action['action'] == 'Bet' or temp_action['action'] == 'Raise':
                    self.raiser_list_river.append(temp_action)

        # 添加待行动的人
        start_abs_postion = 1
        if round.stage == 'preflop':
            if len(self.raiser_list_preflop) == 0: end_abs_postion = (round.dealer_abs_position + 2) % round.max_players # BB
            else: end_abs_postion = self.raiser_list_preflop[-1]['abs_position']
        elif round.stage == 'flop':
            if len(self.raiser_list_flop) == 0: end_abs_postion = round.dealer_abs_position # BTN
            else: end_abs_postion = self.raiser_list_flop[-1]['abs_position']
        elif round.stage == 'turn':
            if len(self.raiser_list_turn) == 0: end_abs_postion = round.dealer_abs_position # BTN
            else: end_abs_postion = self.raiser_list_turn[-1]['abs_position']
        elif round.stage == 'river':
            if len(self.raiser_list_river) == 0: end_abs_postion = round.dealer_abs_position # BTN
            else: end_abs_postion = self.raiser_list_river[-1]['abs_position']

        for i in range(start_abs_postion, end_abs_postion):
            if i in self.quit_list: continue
            if self.round.players[i].status == 'Waitting' or self.round.players[i].status == 'Empty': 
                self.quit_list.append(i)
                continue

            temp_action = {'position': None, 'action': None, 'pot': 0, 'funds': 0, 'abs_position': None}
            temp_action['abs_position'] = i
            temp_action['position'] = round.players[i].position
            temp_action['action'] = round.players[i].status # 'TBD'
            temp_action['pot'] = round.players[i].pot
            temp_action['funds'] = round.players[i].funds
            if temp_action['action'] is not 'TBD': print('status error hands.py 174')

            if round.stage == 'preflop':
                self.actions_list_preflop.append(temp_action)
            elif round.stage == 'flop':
                self.actions_list_flop.append(temp_action)
            elif round.stage == 'turn':
                self.actions_list_turn.append(temp_action)
            elif round.stage == 'river':
                self.actions_list_river.append(temp_action)
        
        # 检查hero在utg,btn,sb,bb,utg上面逻辑是否成立
        # add round, add action_list, add hero_decision  都要更新last_raiser
        # 有raise则last_raiser，无则flop到bb，turn和river到btn


    # 检查无误之后，把round加入rounds_list，再进行后续更新
    def add_round(self, round):
        if self.datacheck() is not True:
            print('Data check failed')
            return False
        
        # 新手牌，初始化hands
        self.new_hands_flag = self.check_new_hands()
        if self.new_hands_flag:
            self.__init__()
            if self.total_players is None and round.stage == 'preflop': 
                self.total_players = sum(1 for player in round.playersV2 if player.is_active or player.status == 'Fold')

        # 判断是否是新阶段
        new_stage_flag = None
        if not self.rounds_list or round.stage != self.rounds_list[-1].stage:
            new_stage_flag = True
        else:
            new_stage_flag = False
        
        if new_stage_flag and round.stage != 'preflop':
            self.make_up_last_round(round)
        
        self.rounds_list.append(round)
        self.add_actions_list(round, new_stage_flag)
        return True
    
    def check_new_hands(self, round):
        flag = False
        if len(round.publicly_cards) == 0 and any(player.pot == round.small_blind for player in round.playersV2) and any(player.pot == round.big_blind for player in round.playersV2):
            flag = True
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