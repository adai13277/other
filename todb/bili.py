import pymysql  
import time  

# 数据库连接配置  
db_config = {  
    'host': 'localhost',  
    'user': 'root',  # 替换为你的数据库用户名  
    'password': '123456',  # 替换为你的数据库密码  
    'database': 'media_crawler',  # 替换为你的数据库名称  
    'charset': 'utf8mb4' 
}  

# 连接数据库  
connection = pymysql.connect(**db_config)  

try:  
    with connection.cursor() as cursor:  
        # 插入的SQL语句  
        sql = """  
        INSERT INTO bilibili_video (user_id, nickname, avatar, add_ts, last_modify_ts, video_id, video_type, title, `desc`, create_time, liked_count, video_play_count, video_danmaku, video_comment, video_url, video_cover_url)   
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
        """  
        
        # 控制循环次数的变量  
        num_records = 13  # 生成10条测试数据  
        test_data = []  

        for i in range(1, num_records + 1):  
            user_id = f'user_{i:03}'  
            nickname = f'用户{i}'  
            avatar = f'http://example.com/avatar{i}.png'  
            add_ts = int(time.time())  
            last_modify_ts = int(time.time())  
            video_id = f'video_{i:03}'  
            video_type = '类型A' if i % 2 == 0 else '类型B'  # 偶数为类型A，奇数为类型B  
            title = f'视频标题 {i}'  
            desc = f'这是视频 {i} 的描述内容。'  
            create_time = int(time.time())  
            liked_count = str(i * 10)  # 点赞数，为10的倍数  
            video_play_count = str(i * 100)  # 播放数，为100的倍数  
            video_danmaku = str(i % 50)  # 弹幕数量，0-49  
            video_comment = str(i % 10)  # 评论数量，0-9  
            video_url = f'http://example.com/video/{video_id}'  
            video_cover_url = f'http://example.com/cover/{video_id}.png'  

            # 添加到测试数据列表  
            test_data.append((user_id, nickname, avatar, add_ts, last_modify_ts, video_id, video_type, title, desc, create_time, liked_count, video_play_count, video_danmaku, video_comment, video_url, video_cover_url))  

        # 执行批量插入  
        cursor.executemany(sql, test_data)  

        # 提交事务  
        connection.commit()  
        print(f"成功批量插入 {num_records} 条数据！")  

finally:  
    connection.close()