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
        INSERT INTO weibo_note_comment (user_id, nickname, avatar, gender, profile_url, ip_location, add_ts, last_modify_ts, comment_id, note_id, content, create_time, create_date_time, comment_like_count, sub_comment_count)   
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
        """  
        
        # 控制循环次数的变量  
        num_records = 5832  # 生成10条测试数据  
        test_data = []  

        for i in range(1, num_records + 1):  
            user_id = f'user_{i:03}'  
            nickname = f'用户{i}'  
            avatar = f'http://example.com/avatar{i}.png'  
            gender = random.choice(['男', '女'])  # 随机性别  
            profile_url = f'http://example.com/profile/{user_id}'  
            ip_location = f'城市_{random.randint(1, 10)}'  # 使用随机城市名  
            add_ts = int(time.time())  
            last_modify_ts = int(time.time())  
            comment_id = f'comment_{i:03}'  
            note_id = f'note_{(i % 5) + 1:03}'  # 随机选择一个帖子ID  
            content = f'这是评论 {i} 的内容。'  
            create_time = int(time.time())  
            create_date_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time))  
            comment_like_count = str(random.randint(0, 100))  # 随机生成0-100点赞数  
            sub_comment_count = str(random.randint(0, 10))  # 随机生成0-10回复数  

            # 添加到测试数据列表  
            test_data.append((user_id, nickname, avatar, gender, profile_url, ip_location, add_ts, last_modify_ts, comment_id, note_id, content, create_time, create_date_time, comment_like_count, sub_comment_count))  

        # 执行批量插入  
        cursor.executemany(sql, test_data)  

        # 提交事务  
        connection.commit()  
        print(f"成功批量插入 {num_records} 条数据！")  

finally:  
    connection.close()