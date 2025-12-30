from pynput.mouse import Controller, Button
import time
import math

mouse = Controller()

# 获取当前位置
print("当前位置:", mouse.position)

# 设置画布位置（根据实际调整）
canvas_x, canvas_y = 100, 100

# 绘制圆形
radius = 50
points = 36
for i in range(points + 1):
    angle = 2 * math.pi * i / points
    x = canvas_x + radius * math.cos(angle)
    y = canvas_y + radius * math.sin(angle)
    mouse.position = (x, y)
    time.sleep(0.05)