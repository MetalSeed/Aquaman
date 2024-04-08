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

from src.tools.aqm_utils import get_file_full_name
from src.tools.excel_operations import Excel_Sheet_Op, Range_Chcker

# excel完整路径
excel_path = get_file_full_name('preflop_ranges.xlsx', 'src', 'decisionmaker')

# 初始化Excel_Sheet_Op类
dataframe = Excel_Sheet_Op(excel_path)

# 打印info sheet
dataframe.print_info_sheet()
print(dataframe.get_info_version())

# 打印preflop range ratio
dataframe.print_preflop_range_ratio('open')

# 获取CO位置A9o的决策概率
prob_call, prob_raise, prob_fold = dataframe.get_decision_prob('open', 'A9o', 'CO')
print(prob_call, prob_raise, prob_fold)

# 初始化Range_Chcker类
range_chcker = Range_Chcker(excel_path)
# 检查open sheet是否符合前紧后松
range_chcker.open_range_check('open')



