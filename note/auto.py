# auto_fighter.py
import pyautogui
pyautogui.FAILSAFE = False  # Disable fail-safe
import time
import random
import logging
import threading

# 获取logger实例
logger = logging.getLogger(__name__)

class AutoFighter:
    def getRunTime(self):
        return self.runTime

    #输出配置信息
    def format_config_output(self,config):
        # 1. 提取核心信息
        run_time = config["runTime"]  # 总运行时长（秒）
        action = config["action_sequence"][0]  # 核心动作（假设只有一个）
        shortcuts = [sc for sc in config["SHORTCUTS"] if sc["interval"] != -1]  # 过滤禁用的快捷键
        
        # 2. 构建小白友好描述
        output_lines = []
        output_lines.append("配置文件加载完成")
        func_name = action["function"]
        args = action["args"]
        output_lines.append("  动作：{}，参数：{}".format(func_name, args))
        
        output_lines.append("\n【有效快捷键】（仅显示启用的按键）")
        if not shortcuts:
            output_lines.append("  无启用的快捷键（所有按键已禁用）")
        else:
            for sc in shortcuts:
                key = sc["key"]
                interval_s = sc["interval"]
                output_lines.append(
                    f"  按键【{key}】：每 {interval_s} 秒按1次、"
                )
        
        # 3. 拼接日志输出（用换行符分隔，保持整洁）
        return "\n".join(output_lines)

    def __init__(self,config_arg:str):
        try:
            logger.info("初始化AutoFighter")

            #加载配置
            from config import CONFIGS
            self.shortcuts = CONFIGS[config_arg]["SHORTCUTS"]
            self.action_sequence = []
            self.is_buff  = CONFIGS[config_arg]["is_buff"]
            self.action_sequence.extend(CONFIGS[config_arg]["action_sequence"])

            self.runTime = CONFIGS[config_arg]["runTime"]
            logger.info(f"已加载配置: {self.format_config_output(CONFIGS[config_arg])}")
            
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
                        # logger.debug(f"初始化 {buff_key}: 原间隔={interval}, 新间隔={new_interval}")
                        continue
                
                self.last_release_times[buff_key] = current_time
                
            self.stop_event = threading.Event()
            self.running = True
            logger.info("AutoFighter初始化完成")
        except Exception as e:
            logger.exception("初始化时发生错误:")
            raise



    # ------------------------------ 基础键盘操作 ------------------------------
    def _hold_keys(self, keys:str, t:float):
        """按住keys，持续t后释放"""
        try:
            for key in keys:
                pyautogui.keyDown(key)
            time.sleep(t)
        finally:
            for key in keys:
                try:
                    pyautogui.keyUp(key)
                except:
                    pass  # Ignore errors during key release

    def _press_key(self, key: str, delay: float = 0):
        """按下并释放单个键，可选延迟"""
        pyautogui.press(key)
        time.sleep(delay)

    def _press_keys_continue(self, keys: str, t: float , interval: float = 0.1):
        """不断交替按下keys中的每一个按键，持续t秒，交替间隔默认为0.1"""
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
        return self.stop_event.is_set()

    def request_stop(self):
        self.stop_event.set()
        self.running = False
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

    def toUp(self):

        self._wait(0.35)
        self._hold_keys(['space'],0.18)
        self._hold_keys(['up','d'],0.05)


    def toDown(self):

        self._hold_keys(['down','space'],0.18)

    def recAttack(self,keys:str,t:float):
        '''矩形区域刷怪，用于方便瞬移上下的多层怪情况'''
        arr1 = ['right']
        # arr1.extend(keys)
        arr2 = ['left']
        # arr2.extend(keys)
        # print(arr2)
        self._keys_down(keys)
        self._press_key(['right'],0.5)
        self._press_key(['right'],0.5)
        self._press_key(['space'],0.5)
        self._press_key(['right'],0.5)
        self._press_key(['down'],0.5)
        self._press_key(['left'],0.5)
        self._press_key(['left'],0.5)
        self._press_key(['left'],0.5)
        self._press_key(['up'],0.5)
        # self.toUp()
        # self.attack(['space'],0.2)
        # self.attack(arr2,t)
        # self.attack(['space'],0.2)
        # self.toDown()
        self._keys_up(keys)

    def playDrug1(self,t1:float,t2:float):
        self.playDrug('left',t1)
        self.playDrug('right',t2)

    #火毒刷红船专属定制辅助，先放爆炸再放毒,用来刷红船专用
    def playDrug(self,direction:str,t:float):
        self._keys_down([direction,'d'])
        count = 3
        startT = time.time()
        for i in range(count):
            if time.time() - startT > t:
                continue
            ran = random.random()
            self._press_keys_continue(['a','2'],t/count)
            if ran < 1 :   
            #     #概率上瞬移
                passT = time.time() - startT
                if direction == 'left' and  (passT < 0.5 or (passT >3 and passT < 4.5)):
                    continue 
                if direction == 'right' and  (passT < 1 or passT >2.2 or (passT >2 and passT <3)):
                    continue  
                self._keys_up(['d'])
                # self._wait(0.1)

                self._hold_keys(['space'],0.11)
                self._hold_keys(['up','d'],0.05)

                self._keys_down(['d'])
        self._keys_up([direction,'d'])

    #火毒打白贝贝
    def playBBB(self,direction:str,t:float):
        self._keys_down(['2'])
        # self._keys_down(['left','d'])

        #1.to left
        self._hold_keys(['left','d'],3)
        pass
        #2、to up
        # self.

        #3、to right

        #4、to dowm

    #左右各打几秒，循环5次，最后跳跃一下
    def loop_att(self,keys:str,lt:float,rt:float):
        self._keys_down(keys)

        for i in range(5):
            self._hold_keys(['left'],lt)
            # self._wait(lt)
            self._hold_keys(['right'],rt)
            # self._wait(rt)

        self._keys_up(keys)
        
        self.attack(['space'],0.5)

    #左右循环攻击，持续按住keys,巡回t秒，中间交替按keys1,间隔interval =0.1
    def loop_att2(self,keys:str,t:float,keys1:str,interval:float = 0.1):
        for direction in ['left','right']:
            other_direction = self.get_other_direction(direction)

            self._keys_down(keys)

            self._press_keys_continue(keys1,t,interval)

            self._keys_up(keys)

    #左右循环攻击，弓手刷黑贝贝专用
    def loop_att3(self,keys:str,t:float):
        for direction in ['left','right']:
            for i in range(2):
                other_direction = self.get_other_direction(direction)

                self._keys_down([direction])
                # self._wait(0.4)
                # self._press_key(['space'],0.2)
                self._hold_keys(keys,t)
                # self._press_keys_continue(keys1,t,interval)

                self._keys_up([direction])
        


    #a向闪现dt，b向攻击at
    def loop_att1(self,keys:str,dt:float,at:float):
        self._keys_down(keys)
        for direction in ['left','right']:
            other_direction = self.get_other_direction(direction)
            self.attack([direction,'d'],dt)
            self.attack([other_direction],at)

        self._keys_up(keys)


    # stand_t, 2move_t，-move_t ，牧师刷pw专用
    def loop_mushi_pw(self,stand_t:float,move_t:float):

        for direction in ['left','right']:
            other_direction = self.get_other_direction(direction)

            self.ran_move_attack(['a'],stand_t)

            self.attack([direction,'a','d'],move_t * 1)
            self.ran_move_attack(['a'],move_t * 0.2)
            self.attack([direction,'a','d'],move_t * 1)
            # self.ran_move_attack(['a'],move_t * 0.2)
            self.attack([other_direction,'a','d'],move_t * 0.8)

    #在一个总的tt内，按住keys键，在短时间内快速左右移动,移动范围缩放Scale
    def ran_move_attack(self,keys:str,tt:float,scale:float = 0.8):
        self._keys_down(keys)
        current_time = time.time()
        while time.time() - current_time < tt:
            self.attack(['left'],random.random() * scale)
            self.attack(['right'],random.random() * scale)

        self._keys_up(keys)


    #向direction攻击t1秒后，向另一个方向瞬移t2秒
    def dir_att(self,direction:str,keys:str,t1:float,t2:float):
        other_direction = self.get_other_direction(direction)

        new_keys = keys + [direction]
        self.attack(new_keys,t1)
        self.attack([other_direction,'d'],t2)

    def get_other_direction(self,direction):
        if direction == 'right':
            return 'left'
        else:
            return 'right'

    #在绳子上挂机，避免被踢出游戏，t秒内 爬上/爬下 绳子一下
    def guaji(self,t:float):
        self._press_key(['up'],t)
        self._press_key(['down'],t)


    # ------------------------------ 主循环逻辑 ------------------------------
    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] 自动打怪启动...")
        
        direction = 'left'
        current_time = time.time()

        try:
            while not self.should_stop():
                if self.is_buff:
                    self.apply_buffs1()

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