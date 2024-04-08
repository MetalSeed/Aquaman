import os
import sys
import pandas as pd

# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录（tools）
script_dir = os.path.dirname(script_path)
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
# 降Aquaman子目录添加到sys.path
sys.path.append(grandparent_dir)

from src.tools.aqm_utils import get_file_full_name


class Excel_Sheet_Op:
    def __init__(self, excel_path):
        self.excel_path = excel_path

    def get_decision_prob(self, sheet_name, target_row, primary_column):
        sheet_name = sheet_name
        dataframe = pd.read_excel(self.excel_path, header=[0, 1], sheet_name=sheet_name)
        if ('Hand', 'hand') in dataframe.columns:
            dataframe[('Hand', 'hand')] = dataframe[('Hand', 'hand')].astype(str)
            dataframe[('Hand', 'hand')] = dataframe[('Hand', 'hand')].str.strip()
            dataframe.set_index(('Hand', 'hand'), inplace=True)
        else:
            print("'Hand' column not found. Please check the Excel structure.")

        if target_row in dataframe.index:
            # prob = self.dataframe.loc[target_row, (primary_column, secondary_column)]
            call_prob = dataframe.loc[target_row, (primary_column, 'Call')]
            raise_prob = dataframe.loc[target_row, (primary_column, 'Raise')]
            fold_prob = dataframe.loc[target_row, (primary_column, 'Fold')]
            return call_prob, raise_prob, fold_prob
        else:
            print(f"Row '{target_row}' not found in sheet: {sheet_name} position:{primary_column}")
            return None, None, None
    
    def get_info_version(self):
        try:
            info_sheet = pd.read_excel(self.excel_path, sheet_name='info', index_col=0) # 假设第一列是行标题, 不设置会找不到行标题
            version = info_sheet.loc['version', 'value']
            return version
        except ValueError as e:
            print(f"Error: The 'info' sheet does not exist in {self.excel_path}.")

    def print_info_sheet(self):
        try:
            info_sheet = pd.read_excel(self.excel_path, sheet_name='info')
            print("Successfully read the 'info' sheet.")
            print(info_sheet)
        except ValueError as e:
            print(f"Error: The 'info' sheet does not exist in {self.excel_path}.")
    
    def calc_preflop_range_ratio(self, sheet_name, primary_column):
        range_sheet = pd.read_excel(self.excel_path, header=[0, 1], sheet_name=sheet_name)
        handlist = set(range_sheet[('Hand', 'hand')].astype(str).str.strip().tolist())
        range_number = 0
        for hand in handlist:
            call_prob, raise_prob, fold_prob = self.get_decision_prob(sheet_name, hand, primary_column)
            if len(hand) == 2:
                hand_number = 6
            elif len(hand) == 3:
                if hand[-1] == 's':
                    hand_number = 4
                elif hand[-1] == 'o':
                    hand_number = 16
            range_number += hand_number * (call_prob + raise_prob)
        range_ratio = range_number / (52*51/2)
        return range_ratio
    
    def print_preflop_range_ratio(self, sheet_name, position_list = ['EP', 'MP', 'CO', 'BTN', 'BB']):
        for pos in position_list:
            range_ratio = self.calc_preflop_range_ratio(sheet_name, pos)
            range_ratio_percent = round(range_ratio * 100, 2)
            print(f"{pos} range: {range_ratio_percent}%")


class Range_Chcker(Excel_Sheet_Op):
    def __init__(self, excel_path):
        self.excel_path = excel_path
    
    def open_range_check(self, sheet_name, position_list = ['EP', 'MP', 'CO', 'BTN', 'BB']):
        range_sheet = pd.read_excel(self.excel_path, header=[0, 1], sheet_name=sheet_name)
        handlist = set(range_sheet[('Hand', 'hand')].astype(str).str.strip().tolist())
        correct_flag = True
        for hand in handlist:
            call_prob_list, raise_prob_list, fold_prob_list = [], [], []
            for i in range(len(position_list)):
                call_prob, raise_prob, fold_prob = self.get_decision_prob(sheet_name, hand, position_list[i])
                call_prob_list.append(call_prob)
                raise_prob_list.append(raise_prob)
                fold_prob_list.append(fold_prob)
            for i in range(len(position_list) - 1):
                # 前位的call和raise是后位的子集
                if (call_prob_list[i] + raise_prob_list[i] > call_prob_list[i+1] + raise_prob_list[i+1]):
                    print(f'open_range_check tips: {hand} game prob (call+raise) {position_list[i]} > {position_list[i+1]}')
                    correct_flag = False
        return correct_flag


# # excel完整路径
# excel_path = get_file_full_name('preflop_ranges.xlsx', 'src', 'decisionmaker')

# # 初始化Excel_Sheet_Op类
# dataframe = Excel_Sheet_Op(excel_path)

# # 打印info sheet
# dataframe.print_info_sheet()
# print(dataframe.get_info_version())

# # 打印preflop range ratio
# dataframe.print_preflop_range_ratio('open')

# # 获取CO位置A9o的决策概率
# prob_call, prob_raise, prob_fold = dataframe.get_decision_prob('open', 'A9o', 'CO')
# print(prob_call, prob_raise, prob_fold)

# # 初始化Range_Chcker类
# range_chcker = Range_Chcker(excel_path)
# # 检查open sheet是否符合前紧后松
# range_chcker.open_range_check('open')
