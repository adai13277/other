from pyecharts.charts import Pie
from pyecharts import options as opts

# 生成模拟的情感分类数据
sentiment_data = {
    '正面': 5294,
    '中性': 2391,
    '负面': 3355
}

# 创建Pie对象
pie_chart = Pie()

# 添加数据
pie_chart.add(
    "",
    [list(z) for z in zip(sentiment_data.keys(), sentiment_data.values())],
    radius=["40%", "75%"],
)

# 设置全局配置项
pie_chart.set_global_opts(
    title_opts=opts.TitleOpts(title="情感分类饼图"),
    legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"),
)

# 设置系列配置项
pie_chart.set_series_opts(
    label_opts=opts.LabelOpts(is_show=True, formatter="{b}: {c} ({d}%)"),
)

# 渲染图表到HTML文件
pie_chart.render("sentiment_pie_chart.html")
