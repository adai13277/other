# config.py

import logging

logger = logging.getLogger(__name__)
'''

            "function": "loop_att",
            "args": [['a','d'],0,30]

            "function": "loop_att1",
            "args": [['a'],2,0]

            "function": "dir_att",
            "args": ['right',['a'],18,0.1]
            

            "function": "playDrug1",
            "args": [5,4.5]

            "function": "attack)",
            "args": [['a'],3]


            {
            "function": "attack",
            "args": [['a','right'],3]
            },{
                "function": "attack",
                "args": [['a','left','space'],3]
            }


            # "function": "recAttack",
            # "args": [['a','d'],1]
'''
# 是否释放buff
is_buff = True
action_sequence = [{
            "function": "loop_att1",
            "args": [['a'],2,0]
            }]

# ============================== 快捷键配置 ==============================
# 按游戏内实际设置修改（主键盘/小键盘均可）73
# SHORTCUTS = [
#                 {"key": "q", "interval": 888},
#                 {"key": "w", "interval": 888},
#                 {"key": "e", "interval": 777},
#                 {"key": "r", "interval": 555},
#                 {"key": "t", "interval": 900},
#                 {"key": "y", "interval": 900},
#                 {"key": "6", "interval": 550},
#                 {"key": "7", "interval": 550}
#             ]

# SHORTCUTS = [
#                 {"key": "q", "interval": 888},
#                 {"key": "w", "interval": 888},
#                 {"key": "e", "interval": 666},
#                 {"key": "r", "interval": -1},
#                 {"key": "t", "interval": 900},
#                 {"key": "y", "interval": 900},
#                 {"key": "5", "interval": 300},
#                 {"key": "6", "interval": 550},
#                 {"key": "7", "interval": 550}
#             ]

# 按游戏内实际设置修改（主键盘/小键盘均可）牧师
SHORTCUTS = [
                {"key": "q", "interval": -1},
                {"key": "w", "interval": -1},
                {"key": "e", "interval": 888},
                {"key": "r", "interval": -1},
                {"key": "t", "interval": -1},
                {"key": "y", "interval": 888},
                {"key": "5", "interval": 550},
                {"key": "6", "interval": 550},
                {"key": "7", "interval": 900}
            ]

# # 按游戏内实际设置修改（主键盘/小键盘均可）new role
# SHORTCUTS = [
#                 {"key": "q", "interval": -1},
#                 {"key": "w", "interval": -1},
#                 {"key": "e", "interval": -1},
#                 {"key": "r", "interval": -1},
#                 {"key": "t", "interval": -1},
#                 {"key": "y", "interval": -1},
#                 {"key": "1", "interval": 10},
#                 {"key": "2", "interval": 10},
#                 {"key": "7", "interval": -1}
#             ]

logger.debug("配置加载完成")