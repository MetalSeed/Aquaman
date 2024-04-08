import datetime
import os
import sys
import threading

from loadconfig import load_config, filled_room_config
from src.recognizer.nlth_table import Table
from src.hands_converter.class_hands import Round, Hands

from src.tools.aqm_utils import get_file_full_name


class SolverThread(threading.Thread):
    def __init__(self, window_title, platform, max_player):
        threading.Thread.__init__(self)
        self.window_title = window_title
        self.platform = platform
        self.max_player = max_player

        self.action_performer = None
    
        self.hands = Hands()
        self.table = Table()
        self.auto_act = False # load confing 

        # game logger
    

    def run(self):
        # 补充退出条件
        round = Round()
        
        ready = False
        while not ready: #等到hero行动
            ready = self.table.prr.heroturnshot()
            # 补充 检查 按钮情况，房间情况，筹码情况，人数等
        
        round.table2round(self.table)
        self.hands.add_round(round) # 更新hands信息
        self.hands.print_hands_info()
        
        # 决策 输入hands, strategy
        decision = 'X'

        # log info
            # log.info(
            #     "Equity: " + str(table.equity * 100) + "% -> " + str(int(table.assumedPlayers)) + " (" + str(
            #         int(table.other_active_players)) + "-" + str(int(table.playersAhead)) + "+1) Plr")
            # log.info("Final Call Limit: " + str(d.finalCallLimit) + " --> " + str(table.minCall))
            # log.info("Final Bet Limit: " + str(d.finalBetLimit) + " --> " + str(table.minBet))
            # log.info(
            #     "Pot size: " + str(table.totalPotValue) + " -> Zero EV Call: " + str(round(d.maxCallEV, 2)))
            # log.info("+++++++++++++++++++++++ Decision: " + str(d.decision) + "+++++++++++++++++++++++")
        
        # 执行
        order = input("输入回车确认决策 或 输入人工决策：F X C Rx Enter")
        if order == '':
            mouse_target = decision
        else:
            mouse_target = order
        
        if self.auto_act is True:
            self.action_performer.perform(mouse_target)
            
        
        self.hands.add_hero_action(decision)

        # log and save
        # log.info("=========== round end ===========")



# ==== MAIN PROGRAM =====
def Aquaman():
    load_config() #room, strategy
    print("Aquaman version: " + "111")

    # 配置UI相关
    # 配置logger和exception handler

    # t1 = xxx() # ui_thread()
    # t1.start()

    window, platform, max_player = filled_room_config['window_title'], filled_room_config['platform'], filled_room_config['max_players']
    t2 = SolverThread(window, platform, max_player)
    t2.start()

    try:
        # sys.exit(app.exec_())
        pass
    except:
        print("Exiting...")
        # monitor_signals.exit_thread = True

if __name__ == '__main__':
    Aquaman()

# ==== END OF MAIN PROGRAM =====
