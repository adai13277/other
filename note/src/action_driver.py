import pyautogui
import time
import random
import logging

# 禁用 PyAutoGUI 的安全故障保护
pyautogui.FAILSAFE = False

logger = logging.getLogger(__name__)

def action_meta(desc):
    """
    这是一个装饰器，用于给函数打上“描述”标签。
    它不会改变函数的逻辑，只是给函数增加了一个 _action_desc 属性。
    """
    def decorator(func):
        func._action_desc = desc  # 将描述绑定到函数对象上
        return func
    return decorator

class ActionDriver:
    def __init__(self, stop_event):
        """
        :param stop_event: threading.Event，用于感知外部停止信号
        """
        self.stop_event = stop_event
        self.heartbeat_callback = None
        # 添加一个标志位，防止心跳递归调用
        self._is_processing_heartbeat = False

    def set_heartbeat(self, func):
        """注册心跳回调"""
        self.heartbeat_callback = func

    # ==================== 核心底层逻辑 ====================

    def wait(self, seconds):
        """
        智能等待：
        1. 支持随时响应 stop 信号
        2. 支持执行心跳回调 (检查 Buff)
        3. 修复了负数 sleep 的 bug
        4. 防止心跳递归
        """
        if seconds <= 0:
            return

        end_time = time.time() + seconds
        
        while True:
            # 1. 检查停止信号
            if self.stop_event.is_set():
                break

            now = time.time()
            remaining = end_time - now
            
            # 2. 如果时间到了，退出循环
            if remaining <= 0:
                break
            
            # 3. 执行心跳 (检查 Buff)，但加锁防止递归
            # 如果当前已经在处理心跳（比如正在放Buff调用了wait），则跳过这次检查
            if self.heartbeat_callback and not self._is_processing_heartbeat:
                self._is_processing_heartbeat = True # 上锁
                try:
                    self.heartbeat_callback()
                except Exception as e:
                    logger.error(f"心跳回调执行异常: {e}")
                finally:
                    self._is_processing_heartbeat = False # 解锁
                
                # 心跳执行可能耗时，重新计算剩余时间
                now = time.time()
                remaining = end_time - now
                if remaining <= 0:
                    break

            # 4. 睡眠一小段时间，但绝不超过剩余时间，且绝不为负数
            # max(0, ...) 修复了 ValueError: sleep length must be non-negative
            sleep_time = min(0.1, max(0, remaining))
            if sleep_time > 0:
                time.sleep(sleep_time)

    def press(self, key, delay=0, duration=0.0):
        """按下并释放"""
        if duration > 0:
            pyautogui.keyDown(key)
            self.wait(duration)
            pyautogui.keyUp(key)
        else:
            pyautogui.press(key)
        
        if delay > 0:
            self.wait(delay)

    def hold_keys(self, keys, duration):
        """按住一组键持续一段时间"""
        for key in keys:
            pyautogui.keyDown(key)
        
        self.wait(duration)
        
        for key in keys:
            try:
                pyautogui.keyUp(key)
            except:
                pass

    def keys_down(self, keys):
        for key in keys:
            pyautogui.keyDown(key)

    def keys_up(self, keys):
        for key in keys:
            pyautogui.keyUp(key)

    def get_other_direction(self, direction):
        return 'left' if direction == 'right' else 'right'

    # ==================== 具体的战斗技能逻辑 ====================

    def attack(self, keys, t):
        self.hold_keys(keys, t)

    @action_meta("向direction攻击t1秒后，向另一个方向瞬移t2秒")
    def dir_att(self,direction:str,keys:str,t1:float,t2:float):
        other_direction = self.get_other_direction(direction)

        new_keys = keys + [direction]
        self.attack(new_keys,t1)
        self.attack([other_direction,'d'],t2)

    @action_meta("左右往返移动攻击5次 (最后跳跃)")
    def loop_att(self, keys, lt, rt):
        """左右移动攻击，最后跳一下"""
        self.keys_down(keys)
        for i in range(5):
            if self.stop_event.is_set(): break
            self.hold_keys(['left'], lt)
            self.hold_keys(['right'], rt)
        self.keys_up(keys)
        self.press('space', delay=0.5)

    @action_meta("左右瞬移 + 定点攻击")
    def loop_att1(self, keys, dt, at):
        """A向闪现，B向攻击"""
        self.keys_down(keys)
        for direction in ['left', 'right']:
            if self.stop_event.is_set(): break
            other = self.get_other_direction(direction)
            self.attack([direction, 'd'], dt)
            self.attack([other], at)
        self.keys_up(keys)

    def _press_keys_continue(self, keys: str, t: float , interval: float = 0.1):
        """不断交替按下keys中的每一个按键，持续t秒，交替间隔默认为0.1"""
        tt = 0
        current_time = time.time()
        while time.time() - current_time < t:
            for key in keys:
                self._press_key(key,interval)
                
    #左右循环攻击，持续按住keys,巡回t秒，中间交替按keys1,间隔interval =0.1
    def loop_att2(self,keys:str,t:float,keys1:str,interval:float = 0.1):
        for direction in ['left','right']:
            other_direction = self.get_other_direction(direction)

            self.keys_down(keys)

            self._press_keys_continue(keys1,t,interval)

            self.keys_up(keys)

    @action_meta("定点站桩输出 (弓手专用)")
    def loop_att3(self, keys, t):
        """弓箭手专用"""
        for direction in ['left', 'right']:
            if self.stop_event.is_set(): break
            self.keys_down([direction])
            self.hold_keys(keys, t)
            self.keys_up([direction])
            
    @action_meta("牧师 - 群体治愈/攻击循环")
    def loop_mushi_pw(self, stand_t, move_t):
        """牧师刷PW"""
        for direction in ['left', 'right']:
            if self.stop_event.is_set(): break
            other_direction = self.get_other_direction(direction)
            self.ran_move_attack(['a'], stand_t)
            self.attack([direction, 'a', 'd'], move_t * 1)
            self.ran_move_attack(['a'], move_t * 0.2)
            self.attack([direction, 'a', 'd'], move_t * 1)
            self.attack([other_direction, 'a', 'd'], move_t * 0.8)

    def ran_move_attack(self, keys, tt, scale=0.8):
        self.keys_down(keys)
        current_time = time.time()
        while time.time() - current_time < tt:
            if self.stop_event.is_set(): break
            self.attack(['left'], random.random() * scale)
            self.attack(['right'], random.random() * scale)
        self.keys_up(keys)

    def playDrug(self, direction, t):
        """火毒专用"""
        self.keys_down([direction, 'd'])
        count = 3
        startT = time.time()
        while time.time() - startT < t:
             if self.stop_event.is_set(): break
             self.press(['a', '2'])
             # 防止除以零
             sleep_chunk = t/count if count > 0 else 0.1
             self.wait(sleep_chunk)
        self.keys_up([direction, 'd'])

    def guaji(self, t):
        """挂机防掉线"""
        self.press('up', duration=t)
        self.press('down', duration=t)