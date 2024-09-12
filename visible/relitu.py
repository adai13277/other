from pyecharts.charts import Map
from pyecharts import options as opts

# 生成模拟的舆情数据
sentiment_data = {
    '北京市': 0.8,
    '天津市': 0.6,
    '河北省': 0.5,
    '山西省': 0.4,
    '内蒙古自治区': 0.3,
    '辽宁省': 0.7,
    '吉林省': 0.6,
    '黑龙江省': 0.5,
    '上海市': 0.9,
    '江苏省': 0.8,
    '浙江省': 0.9,
    '安徽省': 0.7,
    '福建省': 0.8,
    '江西省': 0.6,
    '山东省': 0.7,
    '河南省': 0.5,
    '湖北省': 0.6,
    '湖南省': 0.7,
    '广东省': 0.7,
    '广西壮族自治区': 0.6,
    '海南省': 0.5,
    '重庆市': 0.8,
    '四川省': 0.7,
    '贵州省': 0.6,
    '云南省': 0.5,
    '西藏自治区': 0.4,
    '陕西省': 0.6,
    '甘肃省': 0.5,
    '青海省': 0.4,
    '宁夏回族自治区': 0.3,
    '新疆维吾尔自治区': 0.2,
    '台湾省': 0.8,
    '香港特别行政区': 0.9,
    '澳门特别行政区': 0.9
}

# 创建Map对象
map_chart = Map()

# 添加数据
map_chart.add(
    "Sentiment",
    [list(z) for z in zip(sentiment_data.keys(), sentiment_data.values())],
    "china"
)

# 设置全局配置项
map_chart.set_global_opts(
    title_opts=opts.TitleOpts(title="China Sentiment Heatmap"),
    visualmap_opts=opts.VisualMapOpts(
        min_=0,
        max_=1,
        range_color=['#d94e5d', '#eac736', '#50a3ba']
    )
)

# 渲染图表到HTML文件
map_chart.render("sentiment_heatmap.html")
