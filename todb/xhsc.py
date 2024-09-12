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
        INSERT INTO xhs_note_comment (user_id, nickname, avatar, ip_location, add_ts, last_modify_ts, comment_id, create_time, note_id, content, sub_comment_count, pictures, parent_comment_id)   
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
        """  
        
        # 控制循环次数的变量  
        num_records = 3320  # 生成10条测试数据  
        test_data = []  

        for i in range(1, num_records + 1):  
            user_id = f'user_{i:03}'  
            nickname = f'用户{i}'  
            avatar = f'http://example.com/avatar{i}.png'  
            ip_location = f'IP_{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}'  # 随机IP地址  
            add_ts = int(time.time())  
            last_modify_ts = int(time.time())  
            comment_id = f'comment_{i:03}'  
            create_time = int(time.time())  
            note_id = f'note_{random.randint(1, 10):03}'  # 随机选择一个笔记ID  
            content = f'这是评论 {i} 的内容。'  
            sub_comment_count = random.randint(0, 5)  # 随机生成0-5个子评论  
            pictures = f'http://example.com/image{i}.png'  # 随机图片URL  
            parent_comment_id = None  # 假设这些是顶级评论，没有父评论  

            # 添加到测试数据列表  
            test_data.append((user_id, nickname, avatar, ip_location, add_ts, last_modify_ts, comment_id, create_time, note_id, content, sub_comment_count, pictures, parent_comment_id))  

        # 执行批量插入  
        cursor.executemany(sql, test_data)  

        # 提交事务  
        connection.commit()  
        print(f"成功批量插入 {num_records} 条数据！")  

finally:  
    connection.close()