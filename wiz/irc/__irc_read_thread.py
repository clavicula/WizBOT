
# -*- coding: utf-8 -*-

import queue
import threading
import time

from wiz.util.observer import Observable
from wiz.util.thread import ResidentThread



class IRCReadThread(ResidentThread, Observable):
    
    def __init__(self, receiver):
        ResidentThread.__init__(self)
        Observable.__init__(self)
        self.__receiver = receiver
        self.__read_buffer = queue.Queue()
    
    def get_message(self):
        return self.__read_buffer.get()
    
    def process(self):
        if self.__receiver is None:
            return
        
        message = self.__receiver.receive()
        if message:
            for line in message.strip().split('\n'):
                self.__read_buffer.put(line)
                self.notify_observers()



class Receiver(object):
    
    def __init__(self, local_socket, encode = 'UTF-8', buf_size = 4096):
        self.__socket = local_socket
        self.__encode = encode
        self.__buf_size = buf_size
    
    def receive(self):
        result = self.__socket.recv(self.__buf_size)
        return result.decode(self.__encode, errors='ignore') if result is not None else ''

