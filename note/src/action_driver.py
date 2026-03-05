import pyautogui
import time
import random
import logging

# 禁用 PyAutoGUI 的安全故障保护
pyautogui.FAILSAFE = False

logger = logging.getLogger(__name__)

def action_meta(desc):
    """
    这是一个装饰器，用于给函数打上"描述"标签。
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
        # 防止心跳递归调用
        self._is_processing_heartbeat = False
        
        # 记录当前按下的按键集合，用于状态恢复
        self.active_keys = set()
        # 记录因暂停而临时松开的按键
        self.paused_state = []

    def set_heartbeat(self, func):
        """注册心跳回调"""
        self.heartbeat_callback = func

    # ==================== 核心底层逻辑 ====================

    def _register_keys_down(self, keys):
        """内部辅助：记录按键按下并执行"""
        for key in keys:
            self.active_keys.add(key)
            pyautogui.keyDown(key)

    def _register_keys_up(self, keys):
        """内部辅助：记录按键抬起并执行"""
        for key in keys:
            if key in self.active_keys:
                self.active_keys.remove(key)
            try:
                pyautogui.keyUp(key)
            except:
                pass

    def pause_recorded_keys(self):
        """
        【新增】主动暂停：临时松开所有当前记录的按键
        供外部逻辑（如放Buff前）手动调用
        """
        self.paused_state = list(self.active_keys)
        if self.paused_state:
            # logger.debug(f"临时暂停按键: {self.paused_state}")
            for k in self.paused_state:
                pyautogui.keyUp(k)
            # 给游戏一点反应时间消除硬直
            time.sleep(0.05)

    def resume_recorded_keys(self):
        """
        【新增】主动恢复：将暂停前记录的按键重新按下去
        """
        if self.paused_state:
            # logger.debug(f"恢复暂停按键: {self.paused_state}")
            for k in self.paused_state:
                # 只有未停止时才恢复
                if not self.stop_event.is_set():
                    pyautogui.keyDown(k)
            self.paused_state = []

    def wait(self, seconds):
        """
        智能等待：
        1. 支持随时响应 stop 信号
        2. 支持执行心跳回调 (检查 Buff)
        3. 【优化】不再自动松开按键，由心跳回调内部决定是否需要松开
        """
        if seconds <= 0:
            return

        end_time = time.time() + seconds
        
        while True:
            # 1. 检查停止信号
            if self.stop_event.is_set():
                # 停止时，确保松开所有键
                current_active = list(self.active_keys)
                self._register_keys_up(current_active)
                break

            now = time.time()
            remaining = end_time - now
            
            # 2. 如果时间到了，退出循环
            if remaining <= 0:
                break
            
            # 3. 执行心跳 (检查 Buff)
            if self.heartbeat_callback and not self._is_processing_heartbeat:
                self._is_processing_heartbeat = True # 上锁
                try:
                    # 【核心修改】这里不再自动松开 active_keys
                    # 仅仅是调用回调，控制权交给回调函数
                    # 如果回调函数觉得需要放Buff，它自己会调用 pause_recorded_keys
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

            # 4. 睡眠
            sleep_time = min(0.1, max(0, remaining))
            if sleep_time > 0:
                time.sleep(sleep_time)

    def press(self, key, delay=0, duration=0.0):
        """按下并释放"""
        if duration > 0:
            self._register_keys_down([key])
            self.wait(duration) 
            self._register_keys_up([key])
        else:
            pyautogui.press(key)
        
        if delay > 0:
            self.wait(delay)

    def hold_keys(self, keys, duration):
        """按住一组键持续一段时间"""
        self._register_keys_down(keys)
        self.wait(duration)
        self._register_keys_up(keys)

    def keys_down(self, keys):
        self._register_keys_down(keys)

    def keys_up(self, keys):
        self._register_keys_up(keys)

    def get_other_direction(self, direction):
        return 'left' if direction == 'right' else 'right'

    # ==================== 具体的战斗技能逻辑 (保持原有逻辑) ====================

    @action_meta("接管任意按键")
    def attack(self, keys, t):
        self.hold_keys(keys, t)

    @action_meta("向direction攻击t1秒后，向另一个方向瞬移t2秒")
    def dir_att(self,direction:str,keys:str,t1:float,t2:float):
        other_direction = self.get_other_direction(direction)
        new_keys = [keys, direction]
        self.attack(new_keys,t1)
        self.attack([other_direction,'d'],t2)

    @action_meta("站桩专用，按住方向键和技能键左右攻击5次 (最后跳跃一下)")
    def loop_att(self, keys, lt, rt):
        self.keys_down(keys)
        for i in range(5):
            if self.stop_event.is_set(): break
            self.hold_keys(['left'], lt)
            self.hold_keys(['right'], rt)
        self.keys_up(keys)
        self.press('space', delay=0.5)

    @action_meta("法师专用：左右瞬移攻击 + 两端定点攻击")
    def loop_att1(self, keys, dt, at):
        self.keys_down(keys)
        for direction in ['left', 'right']:
            if self.stop_event.is_set(): break
            other = self.get_other_direction(direction)
            self.attack([direction, 'd'], dt)
            self.attack([other], at)
        self.keys_up(keys)

    def _press_key(self, key, interval):
        pyautogui.press(key)
        self.wait(interval)

    def _press_keys_continue(self, keys: str, t: float , interval: float = 0.1):
        current_time = time.time()
        while time.time() - current_time < t:
            for key in keys:
                self._press_key(key, interval)

    def loop_mushi_pw(self,stand_t:float,move_t:float):

        for direction in ['left','right']:
            other_direction = self.get_other_direction(direction)

            self.ran_move_attack(['a'],stand_t)

            self.attack([direction,'a','d'],move_t * 1)
            self.ran_move_attack(['a'],move_t * 0.2)
            self.attack([direction,'a','d'],move_t * 1)
            # self.ran_move_attack(['a'],move_t * 0.2)
            self.attack([other_direction,'a','d'],move_t * 0.8)

    def loop_att2(self,keys:str,t:float,keys1:str,interval:float = 0.1):
        for direction in ['left','right']:
            self.keys_down(keys)
            self._press_keys_continue(keys1,t,interval)
            self.keys_up(keys)

    @action_meta("定点站桩输出 (弓手专用)")
    def loop_att3(self, keys, t):
        for direction in ['left', 'right']:
            if self.stop_event.is_set(): break
            self.keys_down([direction])
            self.hold_keys(keys, t)
            self.keys_up([direction])
            
    @action_meta("法师专用：两边拉怪+中间清怪")
    def mage_attack(self, stand_t, move_t):
        for direction in ['left', 'right']:
            if self.stop_event.is_set(): break
            other_direction = self.get_other_direction(direction)
            self.ran_move_attack(['a'], stand_t)
            self.attack([direction, 'a', 'd'], move_t * 1)
            self.ran_move_attack(['a'], move_t * 0.2)
            self.attack([direction, 'a', 'd'], move_t * 1)
            self.attack([other_direction, 'a', 'd'], move_t * 0.8)

    #在一个总的tt内，按住keys键，在短时间内快速左右移动,移动范围缩放Scale
    def ran_move_attack(self, keys, tt, scale=0.8):
        self.keys_down(keys)
        current_time = time.time()
        while time.time() - current_time < tt:
            if self.stop_event.is_set(): break
            self.attack(['left'], random.random() * scale)
            self.attack(['right'], random.random() * scale)
        self.keys_up(keys)

    def playDrug(self, direction, t):
        self.keys_down([direction, 'd'])
        count = 3
        startT = time.time()
        while time.time() - startT < t:
             if self.stop_event.is_set(): break
             self.press(['a', '2']) 
             sleep_chunk = t/count if count > 0 else 0.1
             self.wait(sleep_chunk)
        self.keys_up([direction, 'd'])

    @action_meta("用于挂机放buff并防掉线，挂在绳子上，间隔t秒上下移动")
    def guaji_buff(self, t):
        self.press('up', duration=t)
        self.press('down', duration=t)

    @action_meta("战士专用 - 单方向长巡回 + 持续攻击")
    def warrior_loop_attack(self, keys, total_time, move_interval, attack_duration):
        for direction in ['left', 'right']:
            if self.stop_event.is_set():
                break
            start_time = time.time()
            while time.time() - start_time < total_time:
                if self.stop_event.is_set():
                    break
                self.hold_keys([direction], move_interval)
                self.hold_keys(keys, attack_duration)