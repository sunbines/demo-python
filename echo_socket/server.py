import asyncore
import socket

class MyServer(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        client_socket, client_address = self.accept()
        print('New client connected:', client_address)
        MyHandler(client_socket)

class MyHandler(asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(1024)
        if data:
            print('Received data:', data.decode())
            self.send(data)
        else:
            self.close()

    def handle_close(self):
        print('Client disconnected:', self.getpeername())
        self.close()

if __name__ == '__main__':
    server = MyServer('localhost', 8000)
    asyncore.loop()