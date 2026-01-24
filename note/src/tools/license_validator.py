import json
import base64
import datetime
import urllib.request
import uuid
import platform
import subprocess
import hashlib
from email.utils import parsedate_to_datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

class LicenseValidator:
    def __init__(self, public_key_input: str, is_path: bool = False):
        """
        初始化验证器
        :param public_key_input: 公钥字符串 (PEM格式) 或 公钥文件路径
        :param is_path: 如果为True，则public_key_input被视为文件路径
        """
        self.public_key_input = public_key_input
        self.is_path = is_path
        self.time_check_url = "http://www.baidu.com" 
        self._public_key = self._load_public_key()

    @staticmethod
    def get_machine_fingerprint() -> str:
        """
        [公开接口] 获取本机机器码 (静态方法，无需实例化即可调用)
        整合了 Windows 序列号和 UUID 哈希，保证生成和验证的一致性
        """
        try:
            # 1. 优先尝试 Windows 硬盘序列号 (更稳定，抗 MAC 地址漂移)
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(
                        ["wmic", "logicaldisk", "get", "volumeserialnumber"],
                        capture_output=True, text=True, timeout=5
                    )
                    # 解析输出，通常是 "VolumeSerialNumber \n XXXX-XXXX"
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        serial = lines[1].strip()
                        if serial:
                            return f"WIN-{serial}"
                except Exception:
                    pass # 降级到方案 2
            
            # 2. 通用备选方案: 基于 MAC 地址的 UUID 哈希
            # 使用 node() 获取 MAC 地址
            mac_address = uuid.getnode()
            # 结合主机名防止完全冲突 (可选)
            node_name = platform.node()
            
            raw_str = f"{node_name}-{mac_address}"
            machine_hash = hashlib.md5(raw_str.encode()).hexdigest().upper()[:12]
            
            return f"MACHINE-{machine_hash}"
            
        except Exception as e:
            return f"ERROR-{str(e)[:8]}"

    def verify(self, license_key_str: str) -> dict:
        """
        [公开接口] 核心验证方法
        """
        result = {"valid": False, "message": "", "expired_at": None}

        try:
            # 1. 基础解析
            if not license_key_str:
                result["message"] = "License 为空"
                return result

            try:
                license_json = json.loads(base64.b64decode(license_key_str).decode('utf-8'))
                payload_bytes = base64.b64decode(license_json['payload'])
                signature_bytes = base64.b64decode(license_json['signature'])
            except Exception as e:
                result["message"] = f"License 格式错误: {str(e)}"
                return result

            # 2. 签名验证
            try:
                self._public_key.verify(
                    signature_bytes,
                    payload_bytes,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            except InvalidSignature:
                result["message"] = "签名验证失败，License 可能已被篡改"
                return result

            # 3. 业务逻辑校验
            data = json.loads(payload_bytes.decode('utf-8'))
            license_fingerprint = data.get('fingerprint')
            expiration_str = data.get('expiration')
            require_device_binding = data.get('require_device_binding', True)
            
            result["expired_at"] = expiration_str
            result["require_device_binding"] = require_device_binding

            # [A] 设备校验
            if require_device_binding:
                if license_fingerprint != "ANY" and license_fingerprint != "ANY_DEVICE":
                    # 调用静态方法获取当前指纹
                    current_fingerprint = self.get_machine_fingerprint()
                    if license_fingerprint != current_fingerprint:
                        result["message"] = (
                            f"设备指纹不匹配\n"
                            f"License绑定: {license_fingerprint}\n"
                            f"当前设备: {current_fingerprint}"
                        )
                        return result

            # [B] 网络时间校验
            if not self._check_expiration(expiration_str):
                result["message"] = f"License 已过期 (有效期至 {expiration_str})"
                return result

            result["valid"] = True
            result["message"] = "验证成功"
            return result

        except Exception as e:
            result["message"] = f"验证异常: {str(e)}"
            return result

    # ================= 私有方法 =================

    def _load_public_key(self):
        try:
            if self.is_path:
                with open(self.public_key_input, "rb") as key_file:
                    return serialization.load_pem_public_key(key_file.read())
            else:
                return serialization.load_pem_public_key(self.public_key_input.encode('utf-8'))
        except Exception as e:
            raise Exception(f"加载公钥失败: {str(e)}")

    def _get_network_time(self):
        try:
            req = urllib.request.Request(self.time_check_url, method='HEAD')
            with urllib.request.urlopen(req, timeout=3) as response:
                date_str = response.headers['Date']
                return parsedate_to_datetime(date_str)
        except:
            return None

    def _check_expiration(self, expiration_str):
        try:
            if len(expiration_str) == 10:
                exp_date = datetime.datetime.strptime(expiration_str, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
            else:
                exp_date = datetime.datetime.strptime(expiration_str, "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            raise Exception(f"时间格式错误: {expiration_str}")
        
        now_time = self._get_network_time()
        
        if now_time is None:
            raise Exception("无法连接网络验证时间")
            
        # 允许 1 天的缓冲期
        if now_time > exp_date + datetime.timedelta(days=1):
            return False
        return True