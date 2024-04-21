import os
import random
import re
import sys

prjroot = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
sys.path.append(prjroot) # 把aqm根目录加入系统路径

from src.tools.excel_operations import Excel_Sheet_Op

import logging
log = logging.getLogger(__name__)

class PreflopDM:
    def derive_preflop_sheet_name(self, action_list, raiser_list, hero_position):
        names = ['OPEN', 'VOPEN', 'V3B', 'V4B'] # cold3B
        positions = ['UTG', 'EP', 'MP', 'CO', 'BTN', 'SB', 'BB']
        name_list = []
        # 区分有效raise，无效raise的all in去掉
        if len(raiser_list) == 0:
            name_list.append('OPEN')
        elif len(raiser_list) == 1:
            # limp vs open
            # vs open
            # 前位的open和后位的open区别对待
            name_list.append('VOPEN')
        elif len(raiser_list) == 2:
            # open vs 3B
            # call vs 3B
            # vs cold3B
            name_list.append('V3B')
        elif len(raiser_list) == 3:
            # open vs 3B 4B
            # 3B vs cold4B
            # 3B vs 4B
            name_list.append('V4B')
        
        hero_position_clear = re.sub(r'\d+', '', hero_position) # 去掉EP或者MP的数字后缀
        name_list.append(hero_position_clear)

        sheet_name = " ".join(name_list) # 用空格把list连接成str
        return sheet_name

    def preflop_analyser(self, hands, strategy_preflop = None):
            stage = 'preflop'
            action_list = hands.actions_lists[stage]
            raiser_list = hands.raisers_lists[stage]
            hero_positon = hands.rounds_list[0].palyers[0].postion_name
            hero_cards = hands.rounds_list[0].players[0].cards

            #设置文件路径并读取
            excel_file = 'decisionmaker/preflop.xlsx'
            sheet_op = Excel_Sheet_Op(excel_file)

            #获取文件版本信息
            excel_version = sheet_op.get_info_version() # 获取范围表的版本
            log.info("Preflop Excelsheet Version: " + str(excel_version))
            
            # 根据策略，对手情况，决定范围表名称
            sheet_name = self.derive_preflop_sheet_name(action_list, raiser_list, hero_positon) # 根据当前牌局情况获取范围表的sheet（call前位和call后位要分开）
            call_prob, raise_prob, fold_prob = sheet_op.get_decision_prob(sheet_name, hero_cards, hero_positon)
            # 根据策略及对手情况，调整概率
            # 根据筹码深度，调整频率。可以按 overpair, pair, ABC, 小结构 来判断赔率是否够，其次再看prob的decision
            pass
            
            # 如果当前手牌在范围表中
            if call_prob is not None:
                rnd = random.random()
                log.debug(f"Random number: {rnd}")
                log.debug(f"Sheet name: {sheet_name}")
                log.debug(f"Call probability: {call_prob}")
                log.debug(f"Raise probability: {raise_prob}")

                # 根据随机数和概率进行决策
                if rnd < call_prob:
                    decision = 'C'
                    log.info('根据范围表，可以跟注')

                elif call_prob <= rnd <= raise_prob + call_prob:
                    decision = 'Bx'
                    log.info('根据范围表，可以加注')
                else:
                    decision = 'F'
                    log.info('根据范围表，应该弃牌')
            else:
                decision = 'F'
                log.info('根据范围表，应该弃牌')

            return decision