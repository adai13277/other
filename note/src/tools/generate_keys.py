from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

def generate_keys():
    # 1. 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. 生成公钥
    public_key = private_key.public_key()

    # 3. 保存私钥 (PEM格式) - 放在服务器端
    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # 4. 保存公钥 (PEM格式) - 分发给客户端
    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print("密钥对已生成：private_key.pem (务必保密), public_key.pem (分发给客户端)")

if __name__ == "__main__":
    generate_keys()
