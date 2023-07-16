import asyncore_debug
import logging
import socket

class MessageClient(asyncore_debug.dispatcher):
    """Sends messages to the server and receives responses."""
    def __init__(self, address, message, chunk_size=1024):
        self.address = address
        self.message = message
        self.to_send = message
        self.chunk_size = chunk_size
        self.logger = logging.getLogger('Client')
        asyncore_debug.dispatcher.__init__(self)
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.logger.debug('connecting to %s', self.address)
        self.connect(self.address)
    
    def handle_error(self):
        self.logger.info('FAILED TO CONNECT. Retrying -> "%s"',self.to_send )
        self.__init__(self.host,self.port,self.to_send)
    
    def handle_connect(self):
        self.logger.debug('client_handle_connect()')
    
    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close() 
    
    def writable(self):
        self.logger.debug('writable() -> %s', bool(self.to_send))
        return bool(self.to_send)

    def handle_write(self):
        data = self.to_send[:self.chunk_size]
        print(self.to_send[:self.chunk_size])
        sent = self.send(data.encode())
        print(sent)
        print(self.to_send[:sent])
        if sent < len(self.to_send):
            self.logger.debug('warning max buffer is %d', self.chunk_size)
        self.logger.debug('handle_write() -> (%d) "%s"', sent, self.to_send[:sent])
        self.to_send = ""

    def handle_read(self):
        data = self.recv(self.chunk_size).decode()
        if bool(data): 
            # sending empty data automatically causes self.handle_close();
            # no need to do it manually:
            # self.handle_close()
            self.logger.debug('handle_read() -> (%d) "%s"', len(data), data)
            print(data)
            

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s',)
    address = "./socket.asok"
    client = MessageClient(address, message='hi, are you the server?')
    # asyncore.loop()
    # modify the message after 2s
    asyncore_debug.loop(count=2) # 20 x 0.1s = 2s 

