import time
import logging
import threading
import json
import os
import sys
from action_driver import ActionDriver

logger = logging.getLogger(__name__)

class AutoFighter:
    def __init__(self):
        logger.info("初始化 AutoFighter 控制器")
        self.stop_event = threading.Event()
        self.running = True
        
        # 1. 实例化动作驱动器 (Hand)
        self.driver = ActionDriver(self.stop_event)
        
        # 2. 将 Sync Buff 的检查逻辑注册给驱动器
        # 这样驱动器在执行长时间动作(如 wait 或 hold_keys)时，会自动回调这里
        self.driver.set_heartbeat(self.check_sync_buffs)

        # 3. 读取配置
        self.load_config_from_json()
        
        # 4. 初始化 Buff 计时器
        self.init_buff_timers()
        
    def load_config_from_json(self):
        config_path = 'config.json'
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            config_path = os.path.join(base_path, 'config.json')

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                full_json = json.load(f)
            
            use_config = full_json.get("use_config", "1")
            all_configs = full_json.get("configs", {})

            if use_config not in all_configs:
                raise ValueError(f"配置编号 {use_config} 不存在")
                
            config = all_configs[use_config]
            
            self.shortcuts = config["SHORTCUTS"]
            self.action_sequence = config["action_sequence"]
            self.is_buff = config["is_buff"]
            self.runTime = config["runTime"]
            
            logger.info(f"已加载配置 [{use_config}]: {config.get('_desc', '无描述')}")
        except Exception as e:
            logger.error(f"读取配置失败: {e}")
            raise


    def init_buff_timers(self):
        """
        Buff 分类逻辑 v3 (最终版):
        1. interval < 0: 禁用 (跳过)
        2. interval < 100: 强制归为无间隔 (线程执行)
        3. interval >= 100:
           - 尾数为 0: 无间隔 (线程执行)
           - 尾数非 0: 有间隔 (主循环同步执行)
        """
        self.last_release_times = {}
        self.threaded_shortcuts = [] 
        self.sync_shortcuts = []     

        current_time = time.time()
        for conf in self.shortcuts:
            raw_interval = conf["interval"] 
            buff_key = conf["key"]
            
            # --- 规则1: 负数直接过滤 ---
            if raw_interval < 0:
                continue

            # --- 规则2: 小于 100 的统统进线程 ---
            if raw_interval < 100:
                self.threaded_shortcuts.append({"key": buff_key, "interval": raw_interval})
                self.last_release_times[buff_key] = current_time - raw_interval
                continue

            # --- 规则3: 大于等于 100 的逻辑 ---
            final_interval = raw_interval
            if raw_interval <= 999: 
                str_num = str(raw_interval)
                if len(str_num) == 3 and str_num[1] == str_num[0]:
                    hundreds = int(str_num[0]) * 100
                    tens = int(str_num[1]) * 10
                    offset = 0 if str_num[2] != '0' else -5
                    final_interval = hundreds + tens + offset
            
            self.last_release_times[buff_key] = current_time - final_interval

            if raw_interval % 10 == 0:
                self.threaded_shortcuts.append({"key": buff_key, "interval": final_interval})
            else:
                self.sync_shortcuts.append({"key": buff_key, "interval": final_interval})
        
        # ================== 用户友好型输出逻辑 ==================
        msg = "\n" + "="*40 + "\n"
        msg += "        Buff 系统加载报告\n"
        msg += "="*40 + "\n"

        msg += "【1】极速模式 (独立线程/无视动作硬直):\n"
        if not self.threaded_shortcuts:
            msg += "   (无)\n"
        else:
            for item in self.threaded_shortcuts:
                desc = "无间隔连点" if item['interval'] == 0 else f"每 {item['interval']} 秒"
                msg += f"   ► 按键 [{item['key'].upper()}] : {desc}\n"

        msg += "\n【2】同步模式 (主循环/等待动作空闲):\n"
        if not self.sync_shortcuts:
            msg += "   (无)\n"
        else:
            for item in self.sync_shortcuts:
                msg += f"   ► 按键 [{item['key'].upper()}] : 每 {item['interval']} 秒 (安全释放)\n"
        
        msg += "="*40
        logger.info(msg)

        
    def getRunTime(self):
        return self.runTime

    def should_stop(self):
        return self.stop_event.is_set()

    def request_stop(self):
        self.stop_event.set()
        self.running = False

    # ------------------------------ Buff 逻辑 ------------------------------
    
    # 逻辑1：独立线程运行 (对应尾数为0的配置)
    def run_threaded_buffs(self):
        """
        专门处理尾数为0的Buff。
        修复：必须严格检查时间间隔，防止刷屏。
        """
        if not self.is_buff or not self.threaded_shortcuts:
            logger.info("无符合条件的线程Buff，监控停止")
            return

        logger.info("启动线程 Buff 监控")
        try:
            while not self.should_stop():
                current_time = time.time()
                for conf in self.threaded_shortcuts:
                    buff_key = conf["key"]
                    interval = conf["interval"]
                    
                    # 严格的时间检查！
                    # 如果 interval 是 0，则真的无间隔一直按 (小心使用)
                    # 如果 interval 是 900，则每 900 秒按一次
                    if current_time - self.last_release_times.get(buff_key, 0) >= interval:
                        self.last_release_times[buff_key] = current_time
                        
                        # 调用 driver 按键
                        # 使用 press，不带延迟，实现"无硬直"效果
                        self.driver.press(buff_key)
                        
                        # 简单的日志记录，避免刷屏
                        if interval > 1: 
                            logger.info(f"线程释放无硬直Buff: {buff_key}")

                # 保持 0.1s 心跳，避免 CPU 100%
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"线程Buff异常: {e}")

    # 逻辑2：被 driver 回调 (对应尾数非0的配置)
    def check_sync_buffs(self):
        """
        在主循环间隙调用。
        处理有硬直的 Buff (需要暂停移动来释放)。
        """
        if not self.is_buff:
            return

        current_time = time.time()
        for conf in self.sync_shortcuts:
            buff_key = conf["key"]
            interval = conf["interval"]
            
            if current_time - self.last_release_times.get(buff_key, 0) >= interval:
                self.last_release_times[buff_key] = current_time
                logger.info(f"主循环释放硬直Buff: {buff_key}")
                
                # 模拟硬直：暂停 -> 按键 -> 暂停
                time.sleep(0.5)
                # 使用 duration 模拟长按或等待，确保技能放出来
                self.driver.press(buff_key, duration=0.5)

    # ------------------------------ 主循环 ------------------------------
    def run(self):
        # 获取当前配置的总体描述 (依然从 JSON 读取配置名的描述)
        scheme_desc = self.current_desc if hasattr(self, 'current_desc') else '未命名配置'
        logger.info(f"战斗逻辑启动 | 当前方案: {scheme_desc}")
        
        try:
            while not self.should_stop():
                # 遍历执行配置中的动作序列
                for action in self.action_sequence:
                    if self.should_stop(): break
                    
                    func_name = action["function"]
                    args = action.get("args", [])
                    
                    # 1. 从 driver 中获取函数对象
                    func = getattr(self.driver, func_name, None)
                    
                    if callable(func):
                        # 2. 【核心修改】尝试获取函数上绑定的描述
                        # 如果开发人员忘了加装饰器，则默认显示函数名
                        action_desc = getattr(func, '_action_desc', f"执行指令: {func_name}")
                        
                        # 3. 输出日志
                        # INFO 给小白看
                        logger.info(f"正在执行: {action_desc}")
                        # DEBUG 给开发看参数
                        logger.debug(f"指令详情: {func_name} | 参数: {args}")
                        
                        # 4. 执行函数
                        func(*args)
                    else:
                        logger.warning(f"配置错误: 找不到指令 [{func_name}]，跳过。")
                
                # 动作间隙等待
                self.driver.wait(0.1)
                
        except Exception as e:
            logger.error(f"战斗循环发生异常: {e}", exc_info=True)
        finally:
            logger.info("战斗逻辑已停止")