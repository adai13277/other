#main.py

import logging
import traceback
import sys
import threading
import os
import time

# 配置日志系统
def setup_logging():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    log_file = os.path.join(base_path, 'auto_fighter.log')
    
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filemode='w'
    )

    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 文件处理器 - 明确指定UTF-8编码
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    logging.info(f"日志文件位置: {log_file}")
    logging.info(f"Python版本: {sys.version}")
    logging.info(f"操作系统: {sys.platform}")
    logging.info(f"当前工作目录: {os.getcwd()}")

# 尝试多种导入方式
try:
    from auto_fighter import AutoFighter
except ImportError as e:
    try:
        # 尝试直接导入
        import auto_fighter
        AutoFighter = auto_fighter.AutoFighter
    except ImportError as e2:
        logging.critical(f"导入auto_fighter失败: {str(e)} | {str(e2)}")
        sys.exit(1)

def main():
    try:
        logging.info("程序启动")
        
        # 检查依赖
        try:
            import pyautogui
            logging.info(f"PyAutoGUI版本: {pyautogui.__version__}")
        except ImportError:
            logging.critical("PyAutoGUI未安装!")
            sys.exit(1)
        
        #配置解析
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--config", type=str, default="default", 
                            help="配置文件名称 (数字表示，从1开始，表示第几个配置)")
        args = parser.parse_args()

        fighter = AutoFighter(args.config)
        
        # 创建停止事件
        stop_event = threading.Event()
        
        # 获取将要运行的时间，如果<0,则不会停止运行
        stop_minutes = fighter.getRunTime() 
        stop_time = time.time() + stop_minutes * 60

        if stop_minutes > 0:
            # 获取当前时间并格式化
            current_time = time.time()
            current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
            
            # 计算并格式化预计结束时间
            end_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stop_time))
    
            # 输出增强版日志
            logging.info(
                f"当前时间: {current_time_str}, \n"
                f"持续时间: {stop_minutes}分钟, \n"
                f"预计结束时间: {end_time_str}\n"
            )
        
        thread1 = threading.Thread(target=fighter.apply_buffs, daemon=True)
        thread2 = threading.Thread(target=fighter.run, daemon=True)

        logging.info("启动线程...")
        thread1.start()
        thread2.start()

        try:
            # 添加停止请求标志
            stop_requested = False
            
            # 监控线程状态
            while thread1.is_alive() or thread2.is_alive():
                # 检查是否到达停止时间且尚未请求停止
                if not stop_requested and stop_minutes > 0 and time.time() >= stop_time:
                    logging.info("到达停止时间，请求线程二停止")
                    fighter.request_stop()  # 调用停止方法
                    stop_requested = True  # 设置标志，防止重复请求
                
                # 等待一段时间再检查
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            logging.info("\n收到中断信号，程序退出")
            current_time = time.time()
            current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
            logging.info(f"\n结束时间为:{current_time_str}")
            if not stop_requested:  # 如果尚未请求停止
                fighter.request_stop()
            sys.exit(0)

        logging.info("所有线程执行完毕！")
    except Exception as e:
        logging.exception("程序发生未处理异常:")
        print("\n程序发生错误，详细信息请查看日志文件")
        time.sleep(10)


if __name__ == "__main__":
    setup_logging()
    main()