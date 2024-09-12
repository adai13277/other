import socket

#HOST = '127.0.0.1'
HOST = '82.156.64.17'  # 服务器的主机地址
PORT = 12345  # 服务器的端口号

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

client_socket.sendall("成功了！".encode("utf-8"))

data = client_socket.recv(1024)
#print(data.decode())
print(f"Received from server: {data.decode()}")

client_socket.close()