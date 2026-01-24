import json
import base64
import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import os

# --- 配置 ---
PRIVATE_KEY_PEM = None  # 可选：如果设置了硬编码私钥，则使用它；否则从文件读取

def set_private_key(private_key_pem):
    """设置硬编码的私钥"""
    global PRIVATE_KEY_PEM
    PRIVATE_KEY_PEM = private_key_pem

def generate_license(device_fingerprint, days_valid=0, hours_valid=0, minutes_valid=0, require_device_binding=True):
    """
    生成 License
    :param device_fingerprint: 目标设备指纹（如果不限制设备，可传入 "ANY" 或特定标识）
    :param days_valid: 有效期天数
    :param hours_valid: 有效期小时数
    :param minutes_valid: 有效期分钟数
    :param require_device_binding: 是否强制绑定设备指纹（此参数将被签署在 License 中）
    """
    try:
        # 1. 加载私钥（优先使用硬编码的，否则从文件读取）
        if PRIVATE_KEY_PEM:
            key_bytes = PRIVATE_KEY_PEM.encode('utf-8') if isinstance(PRIVATE_KEY_PEM, str) else PRIVATE_KEY_PEM
        else:
            with open("private_key.pem", "rb") as key_file:
                key_bytes = key_file.read()
        
        private_key = serialization.load_pem_private_key(
            key_bytes, password=None
        )
    except FileNotFoundError:
        print("错误: 找不到私钥文件且未设置硬编码私钥")
        import traceback
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"错误: 加载私钥失败 {e}")
        import traceback
        traceback.print_exc()
        return None

    # 2. 计算过期时间（精确到分钟）
    now = datetime.datetime.now(datetime.timezone.utc)
    expiration_time = now + datetime.timedelta(days=days_valid, hours=hours_valid, minutes=minutes_valid)
    expiration_str = expiration_time.strftime("%Y-%m-%d %H:%M")
    
    # 3. 组装数据 (包含设备绑定策略)
    payload_data = {
        "fingerprint": device_fingerprint,
        "expiration": expiration_str,
        "require_device_binding": require_device_binding,  # ← 新增：设备绑定策略从这里读取
        "nonce": str(datetime.datetime.now().timestamp()) # 加入随机因子防止完全相同的密文
    }
    
    payload_bytes = json.dumps(payload_data, sort_keys=True).encode('utf-8')

    # 4. 签名
    signature = private_key.sign(
        payload_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # 5. 打包
    license_data = {
        "payload": base64.b64encode(payload_bytes).decode('utf-8'),
        "signature": base64.b64encode(signature).decode('utf-8')
    }
    
    return base64.b64encode(json.dumps(license_data).encode('utf-8')).decode('utf-8')

if __name__ == "__main__":
    # 场景 A: 绑定特定设备
    # target_machine_id = "CPU-BFEBFBFF000906EA"
    # key = generate_license(target_machine_id, 30)
    # print(f"绑定设备的 Key:\n{key}\n")

    # 场景 B: 不限制设备 (通用版)
    # 服务端只要填入约定好的通用字符，或者客户端关闭校验即可
    # key_any = generate_license("ANY", 365)
    # print(f"通用版 Key:\n{key_any}")
    
    print("请在代码中取消注释以生成 License")
