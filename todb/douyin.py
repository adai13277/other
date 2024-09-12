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
        INSERT INTO douyin_aweme (user_id, sec_uid, short_user_id, user_unique_id, nickname, avatar, user_signature, ip_location, add_ts, last_modify_ts, aweme_id, aweme_type, title, `desc`, create_time, liked_count, comment_count, share_count, collected_count, aweme_url)   
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
        """  
        
        # 控制循环次数的变量  
        num_records = 10  # 生成10条测试数据  
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
            aweme_id = f'aweme_{i:03}'  
            aweme_type = '类型A' if i % 2 == 0 else '类型B'  # 偶数为类型A，奇数为类型B  
            title = f'抖音视频标题 {i}'  
            desc = f'这是抖音视频 {i} 的描述内容。'  
            create_time = int(time.time())  
            liked_count = str(i * 10)  # 点赞数，为10的倍数  
            comment_count = str(i % 20)  # 评论数量，0-19  
            share_count = str(i % 5)  # 分享数量，0-4  
            collected_count = str(i % 3)  # 收藏数量，0-2  
            aweme_url = f'http://example.com/aweme/{aweme_id}'  

            # 添加到测试数据列表  
            test_data.append((user_id, sec_uid, short_user_id, user_unique_id, nickname, avatar, user_signature, ip_location, add_ts, last_modify_ts, aweme_id, aweme_type, title, desc, create_time, liked_count, comment_count, share_count, collected_count, aweme_url))  

        # 执行批量插入  
        cursor.executemany(sql, test_data)  

        # 提交事务  
        connection.commit()  
        print(f"成功批量插入 {num_records} 条数据！")  

finally:  
    connection.close()