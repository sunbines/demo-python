import asyncore
import socket

class Client(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
    
    def handle_connect(self):
        print("Connected to the server")

    def handle_close(self):
        print("Connection closed")
        self.close()

    def handle_read(self):
        data = self.recv(1024)
        print("Received:", data.decode())

    def writable(self):
        return False

    def handle_write(self):
        print("write~")

    def send_message(self, message):
        self.send(message.encode())

# 使用示例
if __name__ == '__main__':
    client = Client('localhost', 8000)
    client.send_message("Hello, server!")
    asyncore.loop(count=1)