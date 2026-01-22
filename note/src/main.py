import logging
import threading
import sys
import time
import os


import datetime  # 新增
import ctypes    # 新增 (用于弹窗提示)
from auto_fighter import AutoFighter

# ================= 授权配置区 =================
# 格式: "YYYY-MM-DD", 例如 "2026-02-20"
EXPIRATION_DATE = "2026-02-20" 
# ============================================

def check_expiration():
    """检查是否过期"""
    try:
        expire_dt = datetime.datetime.strptime(EXPIRATION_DATE, "%Y-%m-%d")
        now = datetime.datetime.now()
        
        if now > expire_dt:
            msg = f"试用期已结束 ({EXPIRATION_DATE})。\n请联系管理员获取最新版本。"
            # 尝试使用 Windows 弹窗 (小白用户能直接看到)
            try:
                ctypes.windll.user32.MessageBoxW(0, msg, "授权过期", 0x10)
            except:
                print(f"\n{'='*30}\n{msg}\n{'='*30}\n")
            
            # 记录日志（如果日志系统已启动）
            logging.critical("程序已过期，停止运行。")
            sys.exit(1)
            
        # 计算剩余天数，友好提示
        days_left = (expire_dt - now).days
        logging.info(f"授权有效期至: {EXPIRATION_DATE} (剩余 {days_left} 天)")
        
    except Exception as e:
        # 防止日期格式写错导致程序崩溃，默认放行但报错
        logging.error(f"过期检查逻辑出错: {e}")

def setup_logging():
    # 确定日志路径（兼容 exe）
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    log_file = os.path.join(base_path, 'auto_fighter.log')

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8', mode='w'),
            logging.StreamHandler()
        ]
    )

def main():
    setup_logging()
    
    # 1. 【新增】在程序启动最开始进行检查
    check_expiration()

    try:
        # 1. 初始化 (内部会自动读取 config.json)
        fighter = AutoFighter()
        
        # 2. 计算结束时间
        stop_minutes = fighter.getRunTime()
        stop_timestamp = time.time() + stop_minutes * 60 if stop_minutes > 0 else 0
        
        if stop_minutes > 0:
            end_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stop_timestamp))
            logging.info(f"计划运行时长: {stop_minutes}分钟，预计结束于: {end_str}")
        else:
            logging.info("模式: 无限运行 (手动停止)")

        threads = []

        # 3. 启动无间隔 Buff 线程 (独立线程，随时响应)
        # 即使 is_buff 为 False，该方法内部也会自行判断直接返回，所以这里直接启动即可
        t_buff = threading.Thread(target=fighter.run_threaded_buffs, daemon=True, name="BuffThread")
        threads.append(t_buff)
        t_buff.start()
        
        # 4. 启动主战斗线程 (包含有间隔 Buff 的检测)
        t_run = threading.Thread(target=fighter.run, daemon=True, name="MainLoop")
        threads.append(t_run)
        t_run.start()

        # 5. 主线程监控逻辑
        try:
            while True:
                # 检查主逻辑线程是否存活
                if not t_run.is_alive():
                    logging.warning("主逻辑线程已退出，程序结束")
                    break
                
                # 检查时间限制
                if stop_minutes > 0 and time.time() >= stop_timestamp:
                    logging.info("到达预定结束时间")
                    break
                
                time.sleep(1) 
                
        except KeyboardInterrupt:
            logging.info("收到 Ctrl+C，正在停止...")
        
        # 6. 优雅退出
        fighter.request_stop()
        
        # 等待子线程结束
        for t in threads:
            if t.is_alive():
                t.join(timeout=2)
            
        logging.info("程序已退出")

    except Exception as e:
        logging.critical("程序发生未处理异常", exc_info=True)
        # 发生错误时暂停一下，防止窗口秒关看不到报错
        time.sleep(5)

if __name__ == "__main__":
    main()