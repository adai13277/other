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
        INSERT INTO douyin_aweme_comment (user_id, sec_uid, short_user_id, user_unique_id, nickname, avatar, user_signature, ip_location, add_ts, last_modify_ts, comment_id, aweme_id, content, create_time, sub_comment_count)   
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
        """  
        
        # 控制循环次数的变量  
        num_records = 4645  # 生成10条测试数据  
        test_data = []  

        for i in range(1, num_records + 1):  
            user_id = f'user_{i:03}'  
            sec_uid = f'sec_uid_{i:03}'  
            short_user_id = f'short_user_{i:03}'  
            user_unique_id = f'unique_id_{i:03}'  
            nickname = f'用户{i}'  
            avatar = f'http://example.com/avatar{i}.png'  
            user_signature = f'这是用户{i}的签名'  
            ip_location = f'192.168.1.{i}'  # 模拟IP地址  
            add_ts = int(time.time())  
            last_modify_ts = int(time.time())  
            comment_id = f'comment_{i:03}'  
            aweme_id = f'aweme_{(i % 5) + 1:03}'  # 随机选择一个视频ID  
            content = f'这是评论 {i} 的内容。'  
            create_time = int(time.time())  
            sub_comment_count = str(i % 5)  # 随机生成0-4的回复数  

            # 添加到测试数据列表  
            test_data.append((user_id, sec_uid, short_user_id, user_unique_id, nickname, avatar, user_signature, ip_location, add_ts, last_modify_ts, comment_id, aweme_id, content, create_time, sub_comment_count))  

        # 执行批量插入  
        cursor.executemany(sql, test_data)  

        # 提交事务  
        connection.commit()  
        print(f"成功批量插入 {num_records} 条数据！")  

finally:  
    connection.close()