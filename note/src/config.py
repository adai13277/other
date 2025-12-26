# config.py

import logging

logger = logging.getLogger(__name__)
'''

            "function": "loop_att",
            "args": [['a','d'],0,30],

            "function": "loop_att1",
            "args": [['a'],5,5],

             "function": "dir_att",
            "args": ['right',['a'],16,0.2],
        
'''
action_sequence = [{
            "function": "loop_att1",
            "args": [['a'],5,2],
            "kwargs": {}
        }]

# ============================== 快捷键配置 ==============================
# 按游戏内实际设置修改（主键盘/小键盘均可）
SHORTCUTS = [
                {"key": "q", "interval": 888},
                {"key": "w", "interval": 333},
                {"key": "e", "interval": 777},
                {"key": "r", "interval": -1},
                {"key": "t", "interval": -1},
                {"key": "y", "interval": 900},
                {"key": "6", "interval": -1},
                {"key": "7", "interval": 300}
            ]

logger.debug("配置加载完成")