# config.py

import logging

logger = logging.getLogger(__name__)
'''
            #左右分别打几秒
            "function": "loop_att",
            "args": [['a','d'],0,30]

            #
            "function": "loop_att1",
            "args": [['a'],2,0]

            #标飞左右巡回刷怪专用
            "function": "loop_att2",
            "args": [['a'],['d'],2,0]

            "function": "dir_att",
            "args": ['right',['a'],18,0.1]
            

            "function": "playDrug1",
            "args": [5,4.5]

            "function": "attack",
            "args": [['a'],3]

            牧师刷pw
            "function": "loop_mushi_pw",
            "args": [1,1.2]


            # "function": "recAttack",
            # "args": [['a','d'],1]

            挂机
            "function": "guaji",
            "args": [5]
'''
# 是否释放buff

CONFIGS = {
    "1": {#牧师拆车
        "runTime":-1,
        "is_buff":True,
        "action_sequence": [
        {
            "function": "loop_att1",
            "args": [['a'],2,0]
        }],
        "SHORTCUTS": [
            {"key": "q", "interval": -1},
            {"key": "w", "interval": -1},
            {"key": "e", "interval": 777},
            {"key": "r", "interval": 888},
            {"key": "t", "interval": -1},
            {"key": "y", "interval": 900},
            {"key": "5", "interval": -1},
            {"key": "6", "interval": -1},
            {"key": "7", "interval": -1}
        ]
    },
    "2": {#火毒拆车
        "runTime":-1,
        "is_buff":True,
        "action_sequence": [
        {
            "function": "loop_att1",
            "args": [['a'],2,0]
        }],
        "SHORTCUTS": [
            {"key": "q", "interval": 888},
            {"key": "w", "interval": 888},
            {"key": "e", "interval": 777},
            {"key": "r", "interval": 888},
            {"key": "t", "interval": -1},
            {"key": "y", "interval": 900}, 
            {"key": "6", "interval": -1},
            {"key": "7", "interval": -1}
        ]
    },
    "3": {#飞侠
        "runTime":-1,
        "is_buff":True,
        "action_sequence": [
        {
            "function": "loop_att",
            "args": [['a'],3,3]
        }],
        "SHORTCUTS": [
            {"key": "q", "interval": -1},
            {"key": "w", "interval": 555},
            {"key": "e", "interval": -1},
            {"key": "r", "interval": -1},
            {"key": "t", "interval": -1},
            {"key": "y", "interval": 900}, 
            {"key": "5", "interval": 550},
            {"key": "7", "interval": -1}
        ]
    }
}
# ============================== 快捷键配置 ==============================
# 按游戏内实际设置修改（主键盘/小键盘均可）火毒
# SHORTCUTS = [
#                 {"key": "q", "interval": 888},
#                 {"key": "w", "interval": 888},
#                 {"key": "e", "interval": 777},
#                 {"key": "r", "interval": 555},
#                 {"key": "t", "interval": 900},
#                 {"key": "y", "interval": 900}, 
#                 {"key": "2", "interval": 5},
#                 {"key": "1", "interval": 2}
            # ]

#飞侠
# SHORTCUTS = [
#                 {"key": "q", "interval": 888},
#                 {"key": "w", "interval": 888},
#                 {"key": "e", "interval": 666},
#                 {"key": "r", "interval": -1},
#                 {"key": "t", "interval": 900},
#                 {"key": "y", "interval": 900},
#                 {"key": "5", "interval": 300},
#                 {"key": "6", "interval": 550},
#                 {"key": "7", "interval": 550},
#                 {"key": "1", "interval": 3},
#                 {"key": "2", "interval": 8}

#             ]

# 按游戏内实际设置修改（主键盘/小键盘均可）牧师 拆车
# SHORTCUTS = [
#                 {"key": "q", "interval": -1},
#                 {"key": "w", "interval": -1},
#                 {"key": "e", "interval": 777},
#                 {"key": "r", "interval": 111},
#                 {"key": "t", "interval": -1},
#                 {"key": "y", "interval": -1},
#                 {"key": "5", "interval": -1},
#                 {"key": "6", "interval": -1},
#                 {"key": "7", "interval": -1}
#             ]
# 按游戏内实际设置修改（主键盘/小键盘均可）牧师 刷pw
# SHORTCUTS = [
#                 {"key": "q", "interval": 888},
#                 {"key": "w", "interval": 888},
#                 {"key": "e", "interval": 777},
#                 {"key": "r", "interval": 888},
#                 {"key": "t", "interval": 888},
#                 {"key": "y", "interval": 900},
#                 {"key": "5", "interval": 550},
#                 {"key": "6", "interval": 550},
#                 {"key": "7", "interval": -1}
#             ]

# # 按游戏内实际设置修改（主键盘/小键盘均可）new role
# SHORTCUTS = [
#                 {"key": "q", "interval": -1},
#                 {"key": "w", "interval": 111},
#                 {"key": "e", "interval": -1},
#                 {"key": "r", "interval": -1},
#                 {"key": "t", "interval": -1},
#                 {"key": "y", "interval": -1},
#                 {"key": "1", "interval": -1},
#                 {"key": "2", "interval": -1},
#                 {"key": "7", "interval": -1}
#             ]

logger.debug("配置加载完成")