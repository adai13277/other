# config.py

import logging

logger = logging.getLogger(__name__)

action_sequence = [{
            "function": "loop_att",
            "args": [['a','d'],8,8],
            "kwargs": {}
        }]

# ============================== 快捷键配置 ==============================
# 按游戏内实际设置修改（主键盘/小键盘均可）
SHORTCUTS = [
                {"key": "q", "interval": 113},
                {"key": "w", "interval": 773},
                {"key": "e", "interval": 773},
                {"key": "r", "interval": 666},
                {"key": "t", "interval": -1},
                {"key": "y", "interval": 833},
                {"key": "6", "interval": 550},
                {"key": "7", "interval": 550}
            ]

logger.debug("配置加载完成")