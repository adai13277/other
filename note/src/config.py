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
            

            "function": "playDrug1",
            "args": [8,7.5],
        
'''
action_sequence = [{
            "function": "playDrug1",
            "args": [5,5],
            "kwargs": {}
        }]

# ============================== 快捷键配置 ==============================
# 按游戏内实际设置修改（主键盘/小键盘均可）
SHORTCUTS = [
                {"key": "q", "interval": 888},
                {"key": "w", "interval": 888},
                {"key": "e", "interval": 777},
                {"key": "r", "interval": -1},
                {"key": "t", "interval": 900},
                {"key": "y", "interval": 900},
                {"key": "6", "interval": 550},
                {"key": "7", "interval": 550}
            ]

logger.debug("配置加载完成")