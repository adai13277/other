import pymysql  
import time  
import random  

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
        INSERT INTO xhs_note (user_id, nickname, avatar, ip_location, add_ts, last_modify_ts, note_id, type, title, `desc`, video_url, time, last_update_time, liked_count, collected_count, comment_count, share_count, image_list, tag_list, note_url)   
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
        """  
        
        # 控制循环次数的变量  
        num_records = 19  # 生成10条测试数据  
        test_data = []  

        for i in range(1, num_records + 1):  
            user_id = f'user_{i:03}'  
            nickname = f'用户{i}'  
            avatar = f'http://example.com/avatar{i}.png'  
            ip_location = f'IP_{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}'  # 随机IP地址  
            add_ts = int(time.time())  
            last_modify_ts = int(time.time())  
            note_id = f'note_{i:03}'  
            note_type = random.choice(['normal', 'video'])  # 随机选择笔记类型  
            title = f'笔记标题 {i}'  
            desc = f'这是笔记 {i} 的描述。'  
            video_url = None if note_type == 'normal' else f'http://example.com/video{i}.mp4'  # 仅在视频类型时生成视频链接  
            note_time = int(time.time())  
            last_update_time = int(time.time())  
            liked_count = str(random.randint(0, 100))  # 随机生成0-100的点赞数  
            collected_count = str(random.randint(0, 50))  # 随机生成0-50的收藏数  
            comment_count = str(random.randint(0, 20))  # 随机生成0-20的评论数  
            share_count = str(random.randint(0, 10))  # 随机生成0-10的分享数  
            image_list = f'http://example.com/image{i}.png'  # 笔记封面图片  
            tag_list = f'tag1,tag2,tag3'  # 示例标签列表  
            note_url = f'http://example.com/note/{note_id}'  # 笔记详情页的URL  

            # 添加到测试数据列表  
            test_data.append((user_id, nickname, avatar, ip_location, add_ts, last_modify_ts, note_id, note_type, title, desc, video_url, note_time, last_update_time, liked_count, collected_count, comment_count, share_count, image_list, tag_list, note_url))  

        # 执行批量插入  
        cursor.executemany(sql, test_data)  

        # 提交事务  
        connection.commit()  
        print(f"成功批量插入 {num_records} 条数据！")  

finally:  
    connection.close()