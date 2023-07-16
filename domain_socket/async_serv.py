import asyncore_debug
import logging
import time


class ReverseEchoServer(asyncore_debug.dispatcher):
    """Receives connections and establishes handlers for each client."""
    def __init__(self, address):
        self.logger = logging.getLogger('Server')
        asyncore_debug.dispatcher.__init__(self) 
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.bind(address) 
        self.address = self.socket.getsockname() 
        self.logger.debug('binding to %s', self.address)
        self.listen(1)
        self.set_reuse_addr()

    def timein(self):
        self.start_time = time.time()
        self.logger.debug('init start_time -> %e', self.start_time)

    def handle_accept(self):
        # Called when a client connects to our socket
        client_info = self.accept()
        if client_info is not None:
            # start the timeout clock right away
            self.timein()
            self.logger.debug('handle_accept() -> %s', client_info[1])
            ReverseEchoHandler(client_info[0], self.start_time)
    
    def handle_close(self):
        self.logger.debug('server_handle_close()')
        self.close()

class ReverseEchoHandler(asyncore_debug.dispatcher):
    """Handles echoing messages from a single client. """
    
    def __init__(self, sock, start_time, chunk_size=1024):
        self.start_time = start_time
        # socket quits after 5 seconds of inactivity
        self.timeout = 600
        self.chunk_size = chunk_size
        self.logger = logging.getLogger('Handler%s' % str(sock.getsockname()))
        asyncore_debug.dispatcher_with_send.__init__(self, sock=sock)
        self.data_to_write = []
    
    def timeout_check(self):
        delta_t = time.time() - self.start_time
        if delta_t > self.timeout:
            self.logger.debug('timeout! -> %e %e', delta_t, self.timeout)
            return True
        else:
            self.logger.debug('no timeout -> %e %e', delta_t, self.timeout)
            return False

    def trigger_close(self):
        return self.timeout_check() 

    def writable(self):
        """We want to write if we have received data."""
        # the trigger_close here is a hack 
        response = bool(self.data_to_write) or self.trigger_close()
        self.logger.debug('writable() -> %s', response)
        return response
 
    def handle_write(self):
        """Write as much as possible of the reversed recent message we received."""
        if self.trigger_close(): # hack to timeout socket
            sent = self.send("")
            self.handle_close()
            return
        data1 = self.data_to_write.pop()
        data_temp = data1[:self.chunk_size]
        data_send = data_temp.encode()
        sent = self.send(data_send)
        print(sent)
        self.start_time = time.time()
        if sent < len(data1):
            remaining = data1[sent:]
            self.data_to_write.append(remaining)
            self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent])

    def reverse(self, s):
        s = list(s)
        s.reverse()
        s = "".join(s)
        return s
    
    def handle_read(self):
        """Read an incoming message from the client and put it into our outgoing queue."""
        data1 = self.recv(self.chunk_size)
        print(data1.decode())
        data = data1.decode()
        self.logger.debug('handle_read() -> (%d) "%s"', len(data), data)
        data = self.reverse(data)
        self.data_to_write.insert(0, data)
        if not self.writable(): # empty recv
            self.handle_close()
    
    def handle_close(self): 
        """server close only gets called if client decides or after timeout"""
        self.logger.debug('handle_close()')
        self.close()

if __name__=='__main__':
    import socket
    logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s', )
    log = logging.getLogger('main')
    address = "./socket.asok" 
    server = ReverseEchoServer(address)
    asyncore_debug.loop() 
