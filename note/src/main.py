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
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w'
    )
    
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
        
        fighter = AutoFighter()
        
        thread1 = threading.Thread(target=fighter.apply_buffs, daemon=True)
        thread2 = threading.Thread(target=fighter.run, daemon=True)

        logging.info("启动线程...")
        thread1.start()
        thread2.start()

        try:
            while thread1.is_alive() or thread2.is_alive():
                thread1.join(timeout=0.1)
                thread2.join(timeout=0.1)
        except KeyboardInterrupt:
            logging.info("\n收到中断信号，程序退出")
            sys.exit(0)

        logging.info("所有线程执行完毕！")
    except Exception as e:
        logging.exception("程序发生未处理异常:")
        print("\n程序发生错误，详细信息请查看日志文件")
        time.sleep(10)

if __name__ == "__main__":
    setup_logging()
    main()