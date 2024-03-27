import os
import sys
import logging

logger = logging.getLogger('hands')
logger.setLevel(logging.INFO)

# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(grandparent_dir)

from src.recognizer.nlth_table import Table

class Round(Table):
    def __init__(self):
        super().__init__()
        self.stage = None  # 当前游戏阶段：preflop, flop, turn, river  

    def clear(self):
        self.super().clear()
        self.stage = None

    def post_process_round_data(self):
        self.stage = self.get_stage()
    
    def get_stage(self):
        num_cards = len(self.public_cards)
        if num_cards == 0:
            self.stage = 'preflop'
        elif num_cards == 3:
            self.stage = 'flop'
        elif num_cards == 4:
            self.stage = 'turn'
        elif num_cards == 5:
            self.stage = 'river'
        else:
            self.stage = None
            logger.error(f'Stage calculation failed, cards num:{len(self.public_cards)}')
        return self.stage

    def tabledict2round(self, table_dict): # 通过ir的table字典读取round数据
        # room data
        self.platform = table_dict['platform']
        self.max_players = table_dict['max_players']
        self.big_blind = table_dict['big_blind']
        self.small_blind = table_dict['small_blind']

        # publicly data
        self.pot_total = float(table_dict['pot_total']) if table_dict['pot_total'] is not None else None
        self.pot_last_round = table_dict['pot_last_round'] if table_dict['pot_last_round'] is not None else None
        self.public_cards = table_dict['public_cards']
        self.dealer_abs_position = table_dict['dealer_abs_position']

        for i, player in enumerate(table_dict['players']):
            self.players[i].abs_position = player['abs_position']
            self.players[i].position = player['position']

            self.players[i].have_cards = player['have_cards']
            self.players[i].pot = float(player['pot']) if player['pot'] is not None else None
            self.players[i].funds = float(player['funds']) if player['funds'] is not None else None
            self.players[i].decision = player['decision']
            
            self.players[i].join_hands = player['join_hands']
            self.players[i].active = player['active']
            
            self.players[i].cards = player['cards']
            self.players[i].id = player['id']
        
        # hero button数据
        self.call_value = table_dict['call_value']
        self.bet1_power = table_dict['bet1_power']
        self.bet2_power = table_dict['bet2_power']
        self.bet3_power = table_dict['bet3_power']
        self.bet4_power = table_dict['bet4_power']
        self.bet5_power = table_dict['bet5_power']
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

# add_round（）, decision = make_decision(), add_hero_action(decision)
class Hands():
    def __init__(self):
        # hands数据
        self.new_hands_flag = True  # 是否有新的手牌
        self.total_players = None # 玩家总数
        self.rounds_list = []  # 所有round的列表
        self.quit_list = []  # 退出玩家列表

        # 初始化逻辑省略，使用字典来组织行动列表和加注者列表
        self.actions_lists = {'preflop': [], 'flop': [], 'turn': [], 'river': []}
        self.raisers_lists = {'preflop': [], 'flop': [], 'turn': [], 'river': []} # 加注者列表

    def print_hands_info(self):
        print("Hands Info:")
        print(f"public cards: {self.rounds_list[-1].public_cards}, hero cards: {self.rounds_list[-1].players[0].cards}")
        for stage in ['preflop', 'flop', 'turn', 'river']:
            if self.actions_lists[stage] == []: continue
            print(f"{stage}:") # 打印当前阶段
            print("    Actions Lists:")
            for action in self.actions_lists[stage]:
                action_info = ', '.join(f"{key}: {value}" for key, value in action.items())
                print(f"       {action_info}")
            print("    Raiser Lists:")
            for raiser in self.raisers_lists[stage]:
                raiser_info = ', '.join(f"{key}: {value}" for key, value in raiser.items())
                print(f"       {raiser_info}")

        #####
        # 检查hero在utg,btn,sb,bb,utg上面逻辑是否成立
        # add round, add action_list, add hero_decision  都要更新last_raiser
        # 有raise则last_raiser，无则flop到bb，turn和river到btn

    # 把hero的决策加入到actions_list
    def add_hero_action(self, decision):
        # 获取当前回合和hero
        current_round = self.rounds_list[-1]
        player = current_round.players[0]

        # 初始化temp_action
        temp_action = {
            'position': player.position, 
            'action': None, 
            'pot': 0.0, 
            'funds': 0.0, 
            'abs_position': 0
        }

        # 映射决策到行动
        decision_mapping = {
            'F': ('Fold', player.pot, player.funds),
            'X': ('Check', player.pot, player.funds),
            'C': ('Call', player.pot, player.funds),  # 特殊处理
            # 'R1'至'R5'的处理将在后续添加
        }

        if decision in decision_mapping:
            action, pot, funds = decision_mapping[decision]
            temp_action['action'] = action
            if decision == 'C':  # Call需要特殊处理
                # 寻找最近的加注情况
                if self.raisers_lists[current_round.stage] != []:
                    last_raiser_pot = self.raisers_lists[current_round.stage][-1]['pot']
                    pot_difference = last_raiser_pot - player.pot
                    temp_action['pot'] = last_raiser_pot
                    temp_action['funds'] = player.funds - pot_difference
                else:  # 没有加注，则视为跟注大盲
                    last_raiser_pot = current_round.big_blind
                    pot_difference = last_raiser_pot - player.pot
                    temp_action['pot'] = last_raiser_pot
                    temp_action['funds'] = player.funds - pot_difference
            else:
                temp_action['pot'] = pot
                temp_action['funds'] = funds
        else:
            # 处理'R1'至'R5'
            if decision[0] == 'R':
                raise_level = int(decision[1])
                # 将raise_level映射到对应的power属性
                power_levels = {
                    1: current_round.bet1_power,
                    2: current_round.bet2_power,
                    3: current_round.bet3_power,
                    4: current_round.bet4_power,
                    5: current_round.bet5_power
                }
                # 使用raise_level从字典中获取对应的power
                power = power_levels.get(raise_level, 0)  # 如果raise_level不存在，返回默认值0
                if power == 0: print('Raise level error hands.py 170')
                bet_multiplier = current_round.pot_total * (0.5+power)  # 仅示例，要根据底池算法计算算法有问题 #
                logger.info(f"Raise level: {raise_level}, power: {power}, pot_total: {current_round.pot_total}, bet_multiplier: {bet_multiplier}")
                temp_action['action'] = f'Raise'
                temp_action['pot'] = bet_multiplier
                temp_action['funds'] = player.funds - (bet_multiplier - player.pot)
            else:
                logger.error('add_hero_action: Invalid decision!')
        
        actions_list = self.actions_lists[current_round.stage]

        for i, action_clip in enumerate(reversed(actions_list)):
            if action_clip['abs_position'] == 0 and action_clip['action'] == 'TBD':
                actions_list[-i-1] = temp_action
        
        if decision[0] == 'R':
            raiser_list = self.raisers_lists[current_round.stage]
            raiser_list.append(temp_action)

        

                
    # 补全上一阶段的遗漏行动, make up之后，再把round加入rounds_list
    def make_up_actions_list(self, round):
        stage = self.rounds_list[-1].stage
        actions_list = self.actions_lists[stage]
        raiser_list = self.raisers_lists[stage]

        # preflop没有raiser的情况下 所有人call，其他阶段没有raiser的情况下所有人check
        blind = round.big_blind if stage == 'preflop' else None
        last_pot = raiser_list[-1]['pot'] if raiser_list else blind if blind else 0

        for action in actions_list:
            if action['action'] == 'TBD':
                player_next_round = round.players[action['abs_position']]
                if player_next_round.decision == 'Fold' or not player_next_round.have_cards:
                    action['action'] = 'Fold'
                    self.quit_list.append(action['abs_position'])
                else:
                    action['action'] = 'Call' if last_pot else 'Check'
                    action['pot'] = last_pot
                    action['funds'] = player_next_round.funds + player_next_round.pot
    # 组装行动字典
    def get_action_dict(self, abs_position, round, tbd = False):
        temp_action = {'position': None, 'action': None, 'pot': 0, 'funds': 0, 'abs_position': None}
        temp_action['abs_position'] = abs_position
        temp_action['position'] = round.players[abs_position].position
        if tbd:
            temp_action['action'] = 'TBD'
        else:
            temp_action['action'] = round.players[abs_position].decision
        temp_action['pot'] = round.players[abs_position].pot
        temp_action['funds'] = round.players[abs_position].funds
        return temp_action

    # 遇到空座位的时候，前后位abs_position计算要顺序移动
    def seat_pointer(self, abs_position, offset, round):
        if self.rounds_list != []:
            first_round = self.rounds_list[0]
        else:
            first_round = round
        seat = abs_position
        if offset > 0:
            while offset > 0:
                seat = (seat + 1) % first_round.max_players
                if first_round.players[seat].join_hands is True:
                    offset -= 1
            return seat
        elif offset < 0:
            while offset < 0:
                seat = (seat - 1) % first_round.max_players
                if first_round.players[seat].join_hands is True:
                    offset += 1
            return seat


    def add_actions_raisers_list(self, round, new_stage_flag): 
        stage = round.stage
        actions_list = self.actions_lists[stage]
        raiser_list = self.raisers_lists[stage]

        # 添加已经行动的人: 起点 - max_players
        if new_stage_flag: # new stage
            if stage != 'preflop':
                # start_abs_postion = (round.dealer_abs_position + 1) % round.max_players # SB
                start_abs_postion = self.seat_pointer(round.dealer_abs_position, +1, round) # SB
            else: # 'preflop'
                # start_abs_postion = (round.dealer_abs_position + 3) % round.max_players # UTG
                start_abs_postion = self.seat_pointer(round.dealer_abs_position, +3, round) # UTG
        else: # repeat stage
            start_abs_postion = self.seat_pointer(0, 1, round) # hero 下家

        # 如果hero是起点时，没有已行动者，要跳过循环（新阶段，preflop utg, postflop sb）
        if new_stage_flag and start_abs_postion == 0: start_abs_postion = round.max_players
        end_abs_postion = round.max_players

        for i in range(start_abs_postion, end_abs_postion):
            if i in self.quit_list: continue # 已经出局，跳过
            if round.players[i].join_hands is False: # 没有参与手牌
                self.quit_list.append(i)
                continue
            if round.players[i].decision == 'Fold' or round.players[i].have_cards is False: # 弃牌
                self.quit_list.append(i)

            # add to actions list and raiser list
            temp_action = self.get_action_dict(i, round)
            if new_stage_flag: # new stage直接加到actions_list
                actions_list.append(temp_action)
            else: # repeat stage要把TBD更新成实际行动
                for i, action_clip in enumerate(reversed(actions_list)):
                    if action_clip['abs_position'] == temp_action['abs_position']:
                         if action_clip['action'] == 'TBD':
                            actions_list[-i-1] = temp_action
                         else:
                             actions_list.append(temp_action)
            if temp_action['action'] == 'Bet' or temp_action['action'] == 'Raise' or temp_action['action'] == 'Allin':
                raiser_list.append(temp_action)
        
        # 添加待行动的人，hero - last_actor，要处理0-0的异常
        start_abs_postion = 0
        if len(raiser_list) == 0: 
            if stage == 'preflop':
                # end_abs_postion = (round.dealer_abs_position + 2 + 1) % round.max_players # BB + 1
                end_abs_postion = self.seat_pointer(round.dealer_abs_position, +3, round) # BB + 1
            else:
                # end_abs_postion = round.dealer_abs_position + 1 # BTN + 1
                end_abs_postion = self.seat_pointer(round.dealer_abs_position, +1, round) # BTN + 1
        else: 
            # end_abs_postion = raiser_list[-1]['abs_position'] - 1
            end_abs_postion = self.seat_pointer(raiser_list[-1]['abs_position'], -1, round) # 上一个加注者的上家
        
        # 0 - 0 异常处理
        if len(raiser_list) == 0 and end_abs_postion == 0: # hero上家是最后行动的，utg or sb
            end_abs_postion = round.max_players
        elif len(raiser_list) != 0 and end_abs_postion == 0: # hero下家是最后加注的
            # end_abs_postion = 1
            end_abs_postion = self.seat_pointer(0, 1, round) # hero下家

        for i in range(start_abs_postion, end_abs_postion):
            if i in self.quit_list: continue
            if round.players[i].join_hands is False:
                self.quit_list.append(i)
                continue
            # add to actions list
            temp_action = self.get_action_dict(i, round, True)
            actions_list.append(temp_action)
    

    # 检查无误之后，把round加入rounds_list，再进行后续更新
    def add_round(self, round):        
        # 新手牌，初始化hands
        self.new_hands_flag = self.check_new_hands(round)
        if self.new_hands_flag:
            self.__init__()
            if self.total_players is None and round.stage == 'preflop': 
                self.total_players = sum(1 for player in round.players if player.join_hands is True)

        if self.datacheck(self.new_hands_flag, round) is not True:
            print('Data check failed')
            return False

        # 判断是否是新阶段
        new_stage_flag = None
        
        if not self.rounds_list: 
            new_stage_flag = True
        elif self.rounds_list[-1].stage != round.stage:
            new_stage_flag = True
        else: new_stage_flag = False

        if new_stage_flag is True and round.stage != 'preflop':
            self.make_up_actions_list(round)

        self.add_actions_raisers_list(round, new_stage_flag)
        
        self.rounds_list.append(round)

        if self.new_hands_flag:
            logger.info('New hands')
        if new_stage_flag:
            logger.info('New stage: {}'.format(round.stage))
            if round.stage != 'preflop':
                logger.info('public_cards:{}'.format(round.public_cards))
            
        return True
    
    def check_new_hands(self, round):
        flag = False
        if round.stage == 'preflop' and not self.rounds_list:
            flag = True
        return flag

    def datacheck(self, new_hands_flag, round):
        check_flag = True
        # active历史
        # pot, ttpot, plrpot, plrfunds
        # poker cards
        # jon_hands active
        # 检查数据是否完整
        # 异常save到log和文件，给table发指令
        
        # actionlist里存货与is active 及quit_list里的玩家 校验数量
        # wpk correct， 提高字符串识别准确度，就不用在这里矫正了
        if not new_hands_flag:
            for i in range(round.max_players):
                # 更新join_hands 后重新街识别问题
                round.players[i].join_hands = self.rounds_list[0].players[i].join_hands
                
                # 更新fold之后decision识别准确度问题
                if round.players[i].join_hands is True and round.players[i].have_cards is False:
                    round.players[i].decision = 'Fold' 
        
        # error dicision，active的error 用筹码校验
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