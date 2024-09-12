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
        INSERT INTO weibo_note (user_id, nickname, avatar, gender, profile_url, ip_location, add_ts, last_modify_ts, note_id, content, create_time, create_date_time, liked_count, comments_count, shared_count, note_url)   
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
        """  
        
        # 控制循环次数的变量  
        num_records = 38  # 生成10条测试数据  
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
            note_id = f'note_{i:03}'  
            content = f'这是微博帖子 {i} 的内容。'  
            create_time = int(time.time())  
            create_date_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time))  
            liked_count = str(random.randint(0, 100))  # 随机生成0-100的点赞数  
            comments_count = str(random.randint(0, 10))  # 随机生成0-10的评论数  
            shared_count = str(random.randint(0, 5))  # 随机生成0-5的转发数  
            note_url = f'http://example.com/note/{note_id}'  

            # 添加到测试数据列表  
            test_data.append((user_id, nickname, avatar, gender, profile_url, ip_location, add_ts, last_modify_ts, note_id, content, create_time, create_date_time, liked_count, comments_count, shared_count, note_url))  

        # 执行批量插入  
        cursor.executemany(sql, test_data)  

        # 提交事务  
        connection.commit()  
        print(f"成功批量插入 {num_records} 条数据！")  

finally:  
    connection.close()