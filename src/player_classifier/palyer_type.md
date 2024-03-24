
"""

WSD：
    Won showdown，摊牌获胜率。玩家打到摊牌的时候，获胜的比例。这是检查一名牌手打到摊牌的牌力选择，
    WSD越高，表示这么玩家拥有领先牌力的时候，更喜欢通过摊牌比大小的方式来赢得胜利。相对被动。

WTSD：
    Went to showdown，看到摊牌率。玩家看到翻牌后，持续打到摊牌的比例。这是用来检查玩家看转牌河牌
    的倾向性，WTSD越高，跟注的频率越高。

WWSF：
    Won when saw flop，翻牌后胜率玩家看到翻牌后，取得胜利的比例。WWSF偏高不完全代表翻牌后的技术，
    通常和看翻牌的人数有关，经常参与多人底池，WWSF就会偏低，如果经常参与一对一底池，WWSF就会偏高。

AF：
    Aggression factor，激进系数AF是一个记录对手翻牌后动作的数据，用以判断对手翻牌后的下注加注和跟注
    的比例，可以代表一定的激进程度。AF = [(总下注次数) + (总加注次数)]/ (总跟注次数) 。

AFq：
    Aggression frequency，激进频率AFq是一个记录对手翻牌后下注和加注的频率，严格来说，AFq才是用以
    判断对手翻牌后的激进程度最佳参考。AFq =（总下注+总加注）/ 全部行动（下注+加注+跟注+弃牌）*100

VPIP：
    Voluntarily Put $ In Pot %，翻牌前主动投注入池率（VPIP 是个百分比数据，国内简称为：入池率）
    玩家主动往底池里投钱的频率，大盲位置因为是被规则强制下注，如果大盲过牌而进入翻牌圈，将不计算为VPIP。
    长期统计的 VPIP 会很接近玩家选择的底牌范围，所以经常被用来当作玩家的入池松紧度的判断。

PFR：
    Preflop Raise % ，翻牌前的加注比率（和VPIP一样也是个百分比数据）只要是翻牌前是“加注进池”的动作，都计算为PFR，所以不管是前面有多少人下注或加注，只要玩家加注进池，哪怕是一个玩家加注，另一个玩家再加注（3bet），玩家再再加注（4bet），只要不是跟注进池，都列入 PFR 这项统计。


PFR/VPIP：
    翻牌前主动加注入池率翻牌前第一个行动，采取主动加注入池的比例。玩家把 VPIP 和 PFR 的数值相比较，可以得出一个非常直观的结论，就是对手翻牌前的游戏倾向和激进程度。通常观察这两个数据我们能进行玩家的紧中松、凶跟弱类型分类，进而采取针对性策略。PFR/VPIP 越高，这名玩家主动加注入池的频率越高，属于比较喜欢进攻、掌握主动权的类型。

待完善
flop/turn/river下注频率，与下注牌力
    
flop/turn/river跟注频率，与参与牌力
    WTSD是river的参与频率

flop/turn/river,XR与R频率，对应牌力

每种牌面的行动频率，尺度与牌力



WTSD
    表征弃牌率。作为防守方比较有意义。高的话，放心打价值，没牌就过牌。（注意有部分AF高所以WTSD低）
        F   T   R
    AF
        F   T   R
    WTSD
W$SD
    表征是不是实牌,river bet和flop raise, turn raise, river raise意义重大
WWSF, WWST, WWSR won when saw各条街往后的胜率

    
HUD
    F   T   R
W$SD（实牌）
AGG
WTSD(铁头)
WWSx
AF
（进攻的WTSD和防守时的WTSD是不一样的）


当前行动线胜率
    WonHand, Went to ShowDown, Won At ShowDown
3B
FlopB
RiveXR
"""


不同牌面，不同攻守状态（行动线），各条街的AF WTSD WWSD WWSF

LaoDingHUD
https://zhuanlan.zhihu.com/p/362856150


# Aqm HUD
Bange nickname hands 
VPIP  PFR  3B F3B 4B
      Flop Trun Rvier RB 1+ 1+Allin
WWSD
WWSx
AGG
WTSD
      XR   BR   R+B FR TR RR
WWSD
WWSx
AGG
WTSD

CB    Flop Turn River XR XF FR
pub
+pub
-pub
