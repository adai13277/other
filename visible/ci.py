from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pyecharts.charts import WordCloud as PyechartsWordCloud
from pyecharts import options as opts

# 从txt文件中读取文本数据
with open('xiyouji_wuchengen.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# 生成词云
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

# 保存词云图到文件
wordcloud.to_file('wordcloud.png')

# 使用pyecharts生成词云图
words = [
    (word, freq) for word, freq in wordcloud.words_.items()
]

# 创建WordCloud对象
wordcloud_chart = PyechartsWordCloud()

# 添加数据
wordcloud_chart.add(
    "",
    words,
    word_size_range=[20, 100],
    shape="circle"
)

# 设置全局配置项
wordcloud_chart.set_global_opts(
    title_opts=opts.TitleOpts(title="词云图")
)

# 渲染图表到HTML文件
wordcloud_chart.render("wordcloud_chart.html")
