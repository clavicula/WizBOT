
# -*- coding: utf-8 -*-

import queue
import threading
import time

from wiz.util.observer import Observable
from wiz.util.thread import ResidentThread



class IRCReadThread(ResidentThread, Observable):
    
    def __init__(self):
        ResidentThread.__init__(self)
        Observable.__init__(self)
        self.__receiver = None
        self.__read_buffer = queue.Queue()
    
    def get_message(self):
        return self.__read_buffer.get()
    
    def set_receiver(self, receiver):
        self.__receiver = receiver
    
    def _process(self):
        message = self.__receiver.receive()
        if message:
            for line in message.strip().split('\n'):
                self.__read_buffer.put(line)
                self.notify_observers()



class Receiver(object):
    
    def __init__(self, local_socket):
        self.__BUF_SIZE = 4096
        self.__socket = local_socket
    
    def receive(self):
        result = self.__socket.recv(self.__BUF_SIZE)
        if result is not None:
            return result.decode('UTF-8', errors='ignore')
        else:
            return ''

