from pyecharts.charts import Line
from pyecharts import options as opts
from datetime import datetime, timedelta
import random

# 生成模拟的舆情数据
# 假设我们有一个包含7天时间戳和随机舆情数量的列表
start_date = datetime(2023, 1, 1)
end_date = start_date + timedelta(days=6)
dates = [start_date + timedelta(days=i) for i in range(7)]

sentiment_data = {
    '正面': [random.randint(1000, 4000) for _ in range(7)],
    '中性': [random.randint(1000, 4000) for _ in range(7)],
    '负面': [random.randint(1000, 4000) for _ in range(7)],
}

# 创建Line对象
line_chart = Line()

# 添加数据
line_chart.add_xaxis([date.strftime('%Y-%m-%d') for date in dates])
line_chart.add_yaxis("正面", sentiment_data['正面'])
line_chart.add_yaxis("中性", sentiment_data['中性'])
line_chart.add_yaxis("负面", sentiment_data['负面'])

# 设置全局配置项
line_chart.set_global_opts(
    title_opts=opts.TitleOpts(title="时间序列分析折线图"),
    tooltip_opts=opts.TooltipOpts(trigger="axis"),
    xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
    yaxis_opts=opts.AxisOpts(type_="value"),
)

# 渲染图表到HTML文件
line_chart.render("time_series_line_chart.html")
