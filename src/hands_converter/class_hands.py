
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

from src.recognizer.nlth_table import Player, Table
        
class Round(Table):
    def __init__(self):
        super().__init__()
        self.stage = None  # 当前游戏阶段：preflop, flop, turn, river  

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
            print(f'Stage calculation failed, cards num:{len(self.public_cards)}')
        return self.stage

    def tabledict2round(self, table_dict): # 通过ir的table字典读取round数据
        # room data
        self.platform = table_dict['platform']
        self.max_players = table_dict['max_players']
        self.big_blind = table_dict['big_blind']
        self.small_blind = table_dict['small_blind']

        # publicly data
        self.pot_total = table_dict['pot_total']
        self.pot_last_round = table_dict['pot_last_round']
        self.public_cards = table_dict['public_cards']
        self.dealer_abs_position = table_dict['dealer_abs_position']

        for i, player in enumerate(table_dict['players']):
            self.players[i].abs_position = player['abs_position']
            self.players[i].position = player['position']
            self.players[i].have_cards = player['have_cards']
            self.players[i].status = player['status']
            self.players[i].pot = player['pot']
            self.players[i].funds = player['funds']
            self.players[i].cards = player['cards']
            # self.players[i].id = player['id']
        
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

# add_round（）, decision = make_decision(), add_hero_action(decision)
class Hands():
    def __init__(self):
        # hands数据
        self.new_hands_flag = True  # 是否有新的手牌
        self.total_players = None # 玩家总数
        self.quit_list = []  # 退出玩家列表
        self.rounds_list = []  # 所有round的列表
        
        # 初始化逻辑省略，使用字典来组织行动列表和加注者列表
        self.actions_lists = {'preflop': [], 'flop': [], 'turn': [], 'river': []}
        self.raiser_lists = {'preflop': [], 'flop': [], 'turn': [], 'river': []} # 加注者列表

    def print_hands_info(self):
        print("Actions Lists:")
        for stage, actions in self.actions_lists.items():
            print(f"{stage}:") # 打印当前阶段
            for action in actions: # 这里的action应该是个字典
                action_info = ', '.join(f"{key}: {value}" for key, value in action.items())
                print(f"    {action_info}") # 增加缩进以提高可读性

        print("Raiser Lists:")
        for stage, raisers in self.raiser_lists.items():
            print(f"{stage}:") # 打印当前阶段
            for raiser in raisers: # 这里的raiser应该是个字典
                raiser_info = ', '.join(f"{key}: {value}" for key, value in raiser.items())
                print(f"    {raiser_info}") # 增加缩进以提高可读性

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
            'position': None, 
            'action': None, 
            'pot': 0, 
            'funds': 0, 
            'abs_position': player.abs_position
        }

        # 映射决策到行动
        decision_mapping = {
            'F': ('Fold', player.pot, player.funds),
            'X': ('Check', player.pot, player.funds),
            'C': ('Call', None, None),  # 特殊处理
            # 'R1'至'R5'的处理将在后续添加
        }

        if decision in decision_mapping:
            action, pot, funds = decision_mapping[decision]
            temp_action['action'] = action
            if decision == 'C':  # Call需要特殊处理
                # 寻找最近的加注情况
                if current_round.stage in self.raiser_lists and self.raiser_lists[current_round.stage]:
                    last_raiser_pot = self.raiser_lists[current_round.stage][-1]['pot']
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
                bet_multiplier = current_round.pot_total * power  # 仅示例，要根据底池算法计算算法有问题 #
                temp_action['action'] = f'Raise'
                temp_action['pot'] = bet_multiplier
                temp_action['funds'] = player.funds - (bet_multiplier - player.pot)
            else:
                print('Decision error hands.py 355')
        
        actions_list = self.actions_lists[current_round.stage]
        actions_list.append(temp_action)
        if decision[0] == 'R':
            raiser_list = self.raiser_lists[current_round.stage]
            raiser_list.append(temp_action)
                
    # 补全上一阶段的遗漏行动, make up之后，再把round加入rounds_list
    def make_up_actions_list(self, round):
        stage = self.rounds_list[-1].stage
        actions_list = self.actions_lists[stage]
        raiser_list = self.raiser_lists[stage]

        # preflop没有raiser的情况下 所有人call，其他阶段没有raiser的情况下所有人check
        blind = round.big_blind if stage == 'preflop' else None
        last_pot = raiser_list[-1]['pot'] if raiser_list else blind if blind else 0

        for action in actions_list:
            if action['action'] == 'TBD':
                player_next_round = round.players[action['abs_position']]
                if player_next_round.status == 'Fold' or not player_next_round.have_cards:
                    action['action'] = 'Fold'
                    self.quit_list.append(action['abs_position'])
                else:
                    action['action'] = 'Call' if last_pot else 'Check'
                    action['pot'] = last_pot
                    action['funds'] = player_next_round.funds + player_next_round.pot
    # 组装行动字典
    def get_action_dict(self, abs_position, round):
        temp_action = {'position': None, 'action': None, 'pot': 0, 'funds': 0, 'abs_position': None}
        temp_action['abs_position'] = abs_position
        temp_action['position'] = round.players[abs_position].position
        temp_action['action'] = round.players[abs_position].status
        temp_action['pot'] = round.players[abs_position].pot
        temp_action['funds'] = round.players[abs_position].funds
        return temp_action

    def add_actions_list(self, round, new_stage_flag): 
        stage = round.stage
        actions_list = self.actions_lists[stage]
        raiser_list = self.raiser_lists[stage]

        if new_stage_flag: # new stage
            if stage != 'preflop':
                start_abs_postion = (round.dealer_abs_position + 1) % round.max_players # SB
            else: # 'preflop'
                start_abs_postion = (round.dealer_abs_position + 3) % round.max_players # UTG
        else: # repeat stage
            start_abs_postion = 1
        end_abs_postion = round.max_players

        # 添加已经行动的人
        for i in range(start_abs_postion, end_abs_postion):
            if i in self.quit_list: continue # 已经出局，跳过
            if round.players[i].status == 'Waiting' or round.players[i].status == 'Empty': # 入座中
                self.quit_list.append(i)
                continue
            if round.players[i].have_cards is False or round.players[i].status == 'Fold': # 弃牌
                self.quit_list.append(i)

            # add to actions list and raiser list
            temp_action = self.get_action_dict(i, round)
            actions_list.append(temp_action)
            if temp_action['action'] == 'Bet' or temp_action['action'] == 'Raise':
                raiser_list.append(temp_action)
        
        # 添加待行动的人
        start_abs_postion = 1
        if len(raiser_list) == 0: 
            if stage == 'preflop':
                end_abs_postion = (round.dealer_abs_position + 2) % round.max_players # BB
            else:
                end_abs_postion = round.dealer_abs_position # BTN
        else: end_abs_postion = raiser_list[-1]['abs_position'] - 1

        for i in range(start_abs_postion, end_abs_postion):
            if i in self.quit_list: continue
            if round.players[i].status == 'Waiting' or round.players[i].status == 'Empty': 
                self.quit_list.append(i)
                continue
            # add to actions list
            temp_action = self.get_action_dict(i, round)
            actions_list.append(temp_action)
            if temp_action['action'] != 'TBD': print('Error: status is not TBD, hands.py 11231')
    

    # 检查无误之后，把round加入rounds_list，再进行后续更新
    def add_round(self, round):
        if self.datacheck() is not True:
            print('Data check failed')
            return False
        
        # 新手牌，初始化hands
        self.new_hands_flag = self.check_new_hands(round)
        if self.new_hands_flag:
            self.__init__()
            if self.total_players is None and round.stage == 'preflop': 
                self.total_players = sum(1 for player in round.players if player.have_cards or player.status == 'Fold')

        # 判断是否是新阶段
        new_stage_flag = None
        if not self.rounds_list or round.stage != self.rounds_list[-1].stage: new_stage_flag = True
        else: new_stage_flag = False
        
        if new_stage_flag is True and round.stage != 'preflop':
            print(new_stage_flag)
            print(round.stage)
            self.make_up_actions_list(round)

        self.add_actions_list(round, new_stage_flag)
        
        self.rounds_list.append(round)
        return True
    
    def check_new_hands(self, round):
        flag = False
        if len(round.public_cards) == 0 and any(player.pot == round.small_blind for player in round.players) and any(player.pot == round.big_blind for player in round.players):
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