import time
import logging
import threading
import json
import os
import sys

logger = logging.getLogger(__name__)

class AutoFighter:
    def __init__(self):
        logger.info("初始化 AutoFighter 控制器")
        self.stop_event = threading.Event()
        self.running = True
        
        self.start_time = time.time()
        self.buff_start_delay = 5 
        
        # 1. 动态导入动作驱动器
        self.driver = self._load_action_driver()
        
        # 2. 将 Sync Buff 的检查逻辑注册给驱动器
        self.driver.set_heartbeat(self.check_sync_buffs)

        # 3. 读取配置
        self.load_config_from_json()
        
        # 4. 初始化 Buff 计时器
        self.init_buff_timers()

    def _load_action_driver(self):
        """动态加载 ActionDriver 类"""
        import sys
        import os
        import importlib # 引入 importlib
        
        if getattr(sys, "frozen", False):
            base_path = os.path.dirname(sys.executable)
            if base_path not in sys.path:
                sys.path.insert(0, base_path)

        try:
            # 首次导入
            import action_driver
            # 强制重新加载模块（实现修改后重启立即生效，或者支持后续的热更新）
            importlib.reload(action_driver) 
            
            return action_driver.ActionDriver(self.stop_event)
        except ImportError as e:
            logger.error(f"无法导入 action_driver 模块: {e}")
            raise RuntimeError("action_driver.py 文件缺失或导入失败")
        
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
        self.last_release_times = {}
        self.threaded_shortcuts = [] 
        self.sync_shortcuts = []     

        current_time = time.time()
        
        for conf in self.shortcuts:
            raw_interval = conf["interval"] 
            buff_key = conf["key"]
            buff_type = conf.get("type", "non_stun")
            delay_enabled = conf.get("delay_enabled", False)
            
            if isinstance(raw_interval, float):
                raw_interval = int(raw_interval)
            
            if raw_interval < 0:
                continue

            if delay_enabled:
                self.last_release_times[buff_key] = current_time - raw_interval - 10
                status_msg = f"启动5秒后立即释放"
            else:
                self.last_release_times[buff_key] = current_time
                status_msg = f"启动后等待冷却 ({raw_interval}s)"

            if buff_type == "non_stun":
                self.threaded_shortcuts.append({"key": buff_key, "interval": raw_interval, "delay_enabled": delay_enabled})
                logger.info(f"无硬直Buff [{buff_key}] 设定: {status_msg}")
            elif buff_type == "stun":
                self.sync_shortcuts.append({"key": buff_key, "interval": raw_interval, "delay_enabled": delay_enabled})
                logger.info(f"硬直Buff [{buff_key}] 设定: {status_msg}")
        
        logger.info("Buff 系统初始化完成")

    def getRunTime(self):
        return self.runTime

    def should_stop(self):
        return self.stop_event.is_set()

    def request_stop(self):
        self.stop_event.set()
        self.running = False

    # ------------------------------ Buff 逻辑 ------------------------------
    
    def run_threaded_buffs(self):
        """处理无硬直 Buff"""
        if not self.is_buff or not self.threaded_shortcuts:
            return

        logger.info("启动线程 Buff 监控")
        try:
            while not self.should_stop():
                current_time = time.time()
                
                if current_time - self.start_time < 5:
                    time.sleep(0.1)
                    continue
                
                for conf in self.threaded_shortcuts:
                    buff_key = conf["key"]
                    interval = conf["interval"]
                    
                    if current_time - self.last_release_times.get(buff_key, 0) >= interval:
                        self.last_release_times[buff_key] = current_time
                        self.driver.press(buff_key)
                        
                        if interval > 30:
                            logger.info(f"线程Buff释放: {buff_key}")

                time.sleep(0.1)
        except Exception as e:
            logger.error(f"线程Buff异常: {e}")

    def check_sync_buffs(self):
        """
        在主循环间隙调用。
        【核心修改】：只有当真正需要放Buff时，才去暂停攻击
        """
        if not self.is_buff:
            return

        current_time = time.time()
        if current_time - self.start_time < 5:
            return

        # 1. 先检查有哪些 Buff 已经就绪
        pending_buffs = []
        for conf in self.sync_shortcuts:
            buff_key = conf["key"]
            interval = conf["interval"]
            
            if current_time - self.last_release_times.get(buff_key, 0) >= interval:
                pending_buffs.append(conf)

        # 2. 如果没有 Buff 要放，直接返回！
        # 此时 Driver 里的 wait 方法没有收到任何暂停指令，按键会一直保持按下，不会有卡顿。
        if not pending_buffs:
            return

        # 3. 确实有 Buff 要放，现在开始接管控制权
        logger.info(f"检测到Buff就绪: {[b['key'] for b in pending_buffs]}，正在暂停攻击...")
        
        # A. 暂停攻击 (Driver 会记录当前按键并松开)
        self.driver.pause_recorded_keys()
        
        try:
            for conf in pending_buffs:
                if self.should_stop(): break
                
                buff_key = conf["key"]
                
                # 更新时间
                self.last_release_times[buff_key] = current_time
                
                logger.info(f"执行同步Buff: {buff_key}")
                
                # 模拟硬直/等待角色站稳
                time.sleep(0.8) 
                
                # 释放技能 (duration 确保按键有效)
                self.driver.press(buff_key, duration=0.2)
                
                # 后摇缓冲
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"释放Buff时出错: {e}")
        finally:
            # B. 恢复攻击 (Driver 会把刚才暂停的键按回去)
            if not self.should_stop():
                logger.info("Buff释放完毕，恢复攻击")
                self.driver.resume_recorded_keys()

    # ------------------------------ 主循环 ------------------------------
    def run(self):
        scheme_desc = self.current_desc if hasattr(self, 'current_desc') else '未命名配置'
        logger.info(f"战斗逻辑启动 | 当前方案: {scheme_desc}")
        
        try:
            while not self.should_stop():
                for action in self.action_sequence:
                    if self.should_stop(): break
                    
                    func_name = action["function"]
                    args = action.get("args", [])
                    
                    func = getattr(self.driver, func_name, None)
                    
                    if callable(func):
                        action_desc = getattr(func, '_action_desc', f"{func_name}")
                        logger.info(f"执行: {action_desc}")
                        func(*args)
                    else:
                        logger.warning(f"指令 [{func_name}] 不存在，跳过。")
                
                # 动作间隙等待
                self.driver.wait(0.1)
                
        except Exception as e:
            logger.error(f"战斗循环异常: {e}", exc_info=True)
        finally:
            logger.info("战斗逻辑已停止")