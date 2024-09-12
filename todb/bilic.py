 
import pymysql  
import time  

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
        INSERT INTO bilibili_video_comment (user_id, nickname, avatar, add_ts, last_modify_ts, comment_id, video_id, content, create_time, sub_comment_count)   
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
        """  
        
        # 控制循环次数的变量  
        num_records = 3320  # 生成10条测试数据  
        test_data = []  

        for i in range(1, num_records + 1):  
            user_id = f'user_{i:03}'  # 格式化用户ID为user_001, user_002等  
            nickname = f'用户{i}'  
            avatar = f'http://example.com/avatar{i}.png'  
            add_ts = int(time.time())  
            last_modify_ts = int(time.time())  
            comment_id = f'comment_{i:03}'  
            video_id = f'video_{(i % 3) + 1}'  # 生成视频ID为video_1, video_2, video_3  
            content = f'这是{nickname}的评论内容'  
            create_time = int(time.time())  
            sub_comment_count = str(i % 10)  # 生成0到9之间的回复数  

            test_data.append((user_id, nickname, avatar, add_ts, last_modify_ts, comment_id, video_id, content, create_time, sub_comment_count))  

        # 执行批量插入  
        cursor.executemany(sql, test_data)  

        # 提交事务  
        connection.commit()  
        print(f"成功批量插入 {num_records} 条数据！")  

finally:  
    connection.close()