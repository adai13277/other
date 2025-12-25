# auto_fighter.py
import pyautogui
import time
import random
import logging

# 获取logger实例
logger = logging.getLogger(__name__)

# 修复导入问题
try:
    from config import SHORTCUTS, action_sequence
except ImportError as e:
    logger.critical(f"导入config失败: {str(e)}")
    sys.exit(1)

class AutoFighter:
    def __init__(self):
        try:
            logger.info("初始化AutoFighter")
            self.shortcuts = SHORTCUTS
            self.action_sequence = []
            self.action_sequence.append({"function": "apply_buffs1", "args": [], "kwargs": {}})
            self.action_sequence.extend(action_sequence)
            
            self.last_release_times = {}
            current_time = time.time()
            for config in self.shortcuts:
                buff_key = config["key"]
                interval = config["interval"]
                
                if isinstance(interval, int) and interval > 100 and 100 <= interval <= 999:
                    str_num = str(interval)
                    if len(str_num) == 3 and str_num[1] == str_num[0]:
                        hundreds = int(str_num[0]) * 100
                        tens = int(str_num[1]) * 10
                        if str_num[2] != '0':
                            new_interval = hundreds + tens
                        else:
                            new_interval = hundreds + tens - 5
                        
                        self.last_release_times[buff_key] = current_time - new_interval
                        logger.debug(f"初始化 {buff_key}: 原间隔={interval}, 新间隔={new_interval}")
                        continue
                
                self.last_release_times[buff_key] = current_time
                
            self.running = True
            logger.info("AutoFighter初始化完成")
        except Exception as e:
            logger.exception("初始化时发生错误:")
            raise



    # ------------------------------ 基础键盘操作 ------------------------------
    def _press_key(self, key: str, delay: float = 0):
        """按下并释放单个键，可选延迟"""
        pyautogui.press(key)
        time.sleep(delay)

    def _hold_keys(self, keys: str, duration: float = 0):
        """按住键持续一段时间"""
        for key in keys:
            pyautogui.keyDown(key)
    
        # 等待指定时间
        time.sleep(duration)
        
        # 同时释放所有键
        for key in keys:
            pyautogui.keyUp(key)

    def _tap_keys(self, keys: str, t: float , interval: float = 0.1):
        tt = 0
        current_time = time.time()
        while time.time() - current_time < t:
            for key in keys:
                self._press_key(key,interval)

    def _wait(self, seconds: float):
        """等待指定时间"""
        time.sleep(seconds)

    def _keys_down(self,keys:str):
        for key in keys:
            pyautogui.keyDown(key)

    def _keys_up(self,keys:str):
        for key in keys:
            pyautogui.keyUp(key)

    def _hold_press(self, hkeys: str,pkeys:str,duration:float = 3):
        for key in hkeys:
            pyautogui.keyDown(key)

        self._tap_keys(pkeys,duration)
        # 同时释放所有键
        for key in hkeys:
            pyautogui.keyUp(key)


    # ------------------------------ Buff管理 ------------------------------
    #无间隔buff
    def apply_buffs(self):
        """按配置顺序施加所有Buff"""   
        # 检查是否到达Buff间隔
        try:
            while True:
                current_time = time.time()
                for config in self.shortcuts:
                    buff_key = config["key"]
                    interval = config["interval"]
                    if interval <0 or (interval > 100 and interval %10 != 0):
                        continue
                    if current_time - self.last_release_times[buff_key] >= interval:
                        self.last_release_times[buff_key] = current_time

                        self._press_key(buff_key)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n线程1被中断")

    #有间隔buff
    def apply_buffs1(self):
        """按配置顺序施加所有Buff"""   
        # 检查是否到达Buff间隔
        current_time = time.time()
        for config in self.shortcuts:
            buff_key = config["key"]
            interval = config["interval"]
            if interval <0 or interval %10 == 0 or interval < 100:
                continue
            if current_time - self.last_release_times[buff_key] >= interval:
                self.last_release_times[buff_key] = current_time

                self._wait(1)
                self._press_key(buff_key,0.5)

    # ------------------------------ 停止条件 ------------------------------
    def should_stop(self):
        try:
            import keyboard
            return keyboard.is_pressed('esc')  # 直接检测ESC键状态
        except Exception as e:
            logger.error(f"键盘检测失败: {e}")
            return False
    # ------------------------------ 技能释放 ------------------------------
    def attack(self,k,t):
        self._hold_keys(k,t)

    def toLeftRight(self,direction,t,isSunyi:bool = True,isJump:bool =True):
        arr = [direction]
        if isSunyi:
            arr.append('d')
        if isJump:
            arr.append('space')
        self._hold_keys(arr,t)

    def toUp(self,stopArr:str):
        self._keys_up(stopArr)

        self._wait(0.35)
        self._hold_keys(['space'],0.23)
        self._hold_keys(['up','d'],0.05)

        self._keys_down(stopArr)

    #先放爆炸再放毒,用来刷红船专用
    def playDrug(self,direction:str,t:float):
        self._keys_down([direction,'d'])
        count = 8
        startT = time.time()
        for i in range(count):
            if time.time() - startT > t:
                continue
            ran = random.random()
            self._tap_keys(['a','2'],t/count)
            if ran < 1 :   
            #     #概率上瞬移
                passT = time.time() - startT
                if direction == 'left' and  (passT < 0.5 or (passT >3)):
                    continue 
                if direction == 'right' and  (passT < 1.2 or passT >3 or (passT >2 and passT <3)):
                    continue  
                self._keys_up(['d'])
                self._wait(0.35)

                self._hold_keys(['space'],0.25)
                self._hold_keys(['up','d'],0.05)

                self._keys_down(['d'])
        self._keys_up([direction,'d'])

    #火毒打白贝贝
    def playBBB(self,direction:str,t:float):
        self._keys_down(['2'])
        # self._keys_down(['left','d'])

        #1.to left
        self._hold_keys(['left','d'],3)

        #2、to up
        # self.

        #3、to right

        #4、to dowm

        startT = time.time()
        for i in range(count):
            if time.time() - startT > t:
                continue
            ran = random.random()
            self._tap_keys(['a','2'],t/count)
            if ran < 1 :   
            #     #概率上瞬移
                passT = time.time() - startT
                if direction == 'left' and  (passT < 0.5 or (passT >3)):
                    continue 
                if direction == 'right' and  (passT < 1.2 or passT >3 or (passT >2 and passT <3)):
                    continue  
                self._keys_up(['d'])
                self._wait(0.35)

                self._hold_keys(['space'],0.25)
                self._hold_keys(['up','d'],0.05)

                self._keys_down(['d'])
        self._keys_up([direction,'d'])

    def loop_att(self,keys:str,lt:float,rt:float):
        self._keys_down(keys)

        self.attack(['left'],3)
        self.attack(['left'],lt - 3)
        self.attack(['right'],rt)

        self._keys_up(keys)
        if len(keys) == 1:
            self.attack(['down'],0.5)
    # ------------------------------ 主循环逻辑 ------------------------------
    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] 自动打怪启动...")
        
        direction = 'left'
        current_time = time.time()

        try:
            while not self.should_stop():
                for action in self.action_sequence:
                    func_name = action["function"]
                    args = action.get("args", [])
                    kwargs = action.get("kwargs", {})
                    
                    # 获取并调用函数
                    func = getattr(self, func_name, None)
                    if callable(func):
                        print(f"执行: {func_name} 参数: {args} {kwargs}")
                        func(*args, **kwargs)
                    else:
                        print(f"警告: 找不到函数 {func_name}")
                    
                # 短暂等待下一轮循环
                self._wait(0.1)
        
        except KeyboardInterrupt:
            print("程序被用户中断...")
        finally:
            self.running = False
            print(f"[{time.strftime('%H:%M:%S')}] 程序结束")