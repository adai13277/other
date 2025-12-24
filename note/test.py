import pyautogui
import time
import keyboard
from typing import Dict, List

class KeyboardAutoFighter:
    def __init__(self):
        # -------------------------- 核心配置（需根据习惯修改） --------------------------
        # 1. 键位配置（游戏内快捷键）
        self.SKILL_KEYS: Dict[str, str] = {
            "skill1": "a",    # 技能1（如Q/W/E等键盘键）
            "skill2": "s",    # 技能2
            "skill3": "d",    # 技能3（可选扩展）
        }
        self.HP_POTION_KEY: str = "1"  # 吃红药键（建议设为快捷键，如F1）
        self.MP_POTION_KEY: str = "2"  # 吃蓝药键

        # 2. 补给间隔（秒）：定时吃血蓝（按需求调整）
        self.HP_INTERVAL: float = 25    # 每25秒吃红药
        self.MP_INTERVAL: float = 30    # 每30秒吃蓝药 

        # 3. 按键间隔（秒）：**手动设置点按间隔**（例如1秒点按一次）
        self.KEY_PRESS_INTERVAL: float = 1.0  

        # 4. 攻击状态配置（循环逐次点按的组合键）
        # 格式：{"keys": [要点按的键列表]}（无需duration，点按一次即触发）
        self.ATTACK_STATES: List[Dict] = [
            {
                "keys": [self.SKILL_KEYS["skill1"], "left"],  # 技能1 + 左方向键
            },
            {
                "keys": [self.SKILL_KEYS["skill2"], "right"], # 技能2 + 右方向键
            },
            # 可选：扩展第三个状态（比如技能3+左方向键）
            # {
            #     "keys": [self.SKILL_KEYS["skill3"], "left"],
            # }
        ]

        # -------------------------- 状态变量（无需修改） --------------------------
        self.is_paused: bool = False      # 是否暂停
        self.should_stop: bool = False    # 是否停止程序
        self.last_hp_potion: float = 0    # 上次吃红药时间
        self.last_mp_potion: float = 0    # 上次吃蓝药时间

        # 攻击状态相关（循环用）
        self.attack_state_index: int = 0         # 当前攻击状态索引
        self.last_attack_time: float = 0          # 上次点按时间（用于计算间隔）

    def start(self) -> None:
        """启动自动打怪"""
        print("="*50)
        print("冒险岛键盘自动打怪程序已启动！")
        print(f"控制说明：F2=暂停/继续 | ESC=退出 | ]=单次触发攻击（测试用）")
        print(f"攻击逻辑：循环逐次点按{len(self.ATTACK_STATES)}种键盘组合（间隔{self.KEY_PRESS_INTERVAL}秒）")
        print("="*50)

        # 注册全局热键（F2暂停/继续、ESC退出、]单次触发攻击）
        keyboard.add_hotkey("]", self._test_single_attack)  # 新增：单次点按测试
        keyboard.add_hotkey("[", self.stop)
        keyboard.add_hotkey("f2", self.toggle_pause)

        # 初始化状态
        self.is_paused = False
        self.should_stop = False
        self.last_hp_potion = time.time()
        self.last_mp_potion = time.time()
        self.attack_state_index = 0
        self.last_attack_time = time.time()  # 初始化为当前时间，首次点按将在间隔后触发

        # 主循环：每0.1秒检查一次操作（保证响应速度）
        while not self.should_stop:
            if not self.is_paused:
                self._use_consumables()  # 定时吃血蓝
                self._handle_keyboard_attack()  # 处理键盘点按
            time.sleep(0.1)

        print("程序已停止，感谢使用！")

    def _use_consumables(self) -> None:
        """定时吃红/蓝药（纯时间间隔控制，不判断游戏状态）"""
        current_time = time.time()

        # 吃红药
        if current_time - self.last_hp_potion > self.HP_INTERVAL:
            pyautogui.press(self.HP_POTION_KEY)
            self.last_hp_potion = current_time
            print(f"[补给] 吃红药 → {current_time:.1f}秒")

        # 吃蓝药
        if current_time - self.last_mp_potion > self.MP_INTERVAL:
            pyautogui.press(self.MP_POTION_KEY)
            self.last_mp_potion = current_time
            print(f"[补给] 吃蓝药 → {current_time:.1f}秒")

    def _handle_keyboard_attack(self) -> None:
        """循环执行键盘组合点按：定时点按当前状态的键，切换至下一状态"""
        current_time = time.time()
        # 检查是否到达下次点按时间
        if current_time - self.last_attack_time >= self.KEY_PRESS_INTERVAL:
            # 获取当前攻击状态
            current_state = self.ATTACK_STATES[self.attack_state_index]
            # 执行点按操作：按下并松开所有键（模拟逐次点按）
            for key in current_state["keys"]:
                pyautogui.press(key)  # press = 按下 + 松开，即点按一次
                print(f"[攻击] 点按组合：{', '.join(current_state['keys'])}")
            # 切换至下一个状态（循环）
            self.attack_state_index = (self.attack_state_index + 1) % len(self.ATTACK_STATES)
            # 更新上次点按时间
            self.last_attack_time = current_time

    def _test_single_attack(self) -> None:
        """测试用：单次触发当前状态的点按（不切换状态）"""
        current_state = self.ATTACK_STATES[self.attack_state_index]
        for key in current_state["keys"]:
            pyautogui.press(key)
        print(f"[测试] 单次点按：{', '.join(current_state['keys'])}")

    def toggle_pause(self) -> None:
        """切换暂停状态"""
        self.is_paused = not self.is_paused
        status = "继续" if self.is_paused else "暂停"
        print(f"程序已{status}")

    def stop(self) -> None:
        """停止程序（确保松开所有按键，避免残留操作）"""
        # 紧急松开所有可能按住的键（虽然点按不会持续按压，但保险起见）
        for state in self.ATTACK_STATES:
            for key in state["keys"]:
                pyautogui.keyUp(key)
        self.should_stop = True
        print("正在退出程序...")

if __name__ == "__main__":
    fighter = KeyboardAutoFighter()
    try:
        fighter.start()
    except KeyboardInterrupt:
        fighter.stop()