# main.py
from auto_fighter import AutoFighter

def test_consume_items(fighter):
    """测试消耗品使用"""
    print("=== 测试吃红药 ===")
    fighter.use_hp_potion()
    print("=== 测试吃蓝药 ===")
    fighter.use_mp_potion()

def test_buffs(fighter):
    """测试Buff施加"""
    print("=== 测试施加Buff ===")
    fighter.apply_buffs()

def test_skills(fighter):
    """测试技能循环"""
    print("=== 测试技能释放 ===")
    fighter.cast_skill_rotation(times=2)

def test_move(fighter):
    """测试移动"""
    print("=== 测试移动 ===")
    fighter.move("right", duration=2)
    fighter.move("left", duration=2)

if __name__ == "__main__":
    fighter = AutoFighter()
    
    # 运行测试（可选，验证配置是否正确）
    # test_consume_items(fighter)
    # test_buffs(fighter)
    # test_skills(fighter)
    # test_move(fighter)
    

    import threading
    import signal
    import sys

    #无CD buff线程
    thread1 = threading.Thread(target=fighter.apply_buffs, daemon=True)
    #主逻辑线程
    thread2 = threading.Thread(target=fighter.run, daemon=True)

    # 启动线程
    print("开始执行多线程任务...")
    thread1.start()
    thread2.start()

    try:
        while thread1.is_alive() or thread2.is_alive():
            thread1.join(timeout=0.1)
            thread2.join(timeout=0.1)
    except KeyboardInterrupt:
        print("\n收到中断信号，程序退出")
        sys.exit(0)

    print("所有线程执行完毕！")
    # 启动自动打怪
    