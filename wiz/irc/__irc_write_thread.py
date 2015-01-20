
# -*- coding: utf-8 -*-

import re
import queue
import threading
import time

from wiz.util.observer import Observer
from wiz.util.observer import Observable
from wiz.util.thread import ResidentThread



class IRCWriteThread(ResidentThread, Observable, Observer):
    
    def __init__(self, sender):
        ResidentThread.__init__(self)
        Observable.__init__(self)
        self.__lock = threading.RLock()
        self.__sender = sender
        self.__queue = queue.Queue()
    
    def put_message(self, message):
        with self.__lock:
            self.__queue.put(message)
    
    def process(self):
        if self.__sender is None:
            return
        
        with self.__lock:
            while not self.__queue.empty():
                self.__sender.send(self.__queue.get())
        
        # CPUリソース浪費対策
        time.sleep(0.1)
    
    def update(self, target, param = None):
        message = target.get_message()
        result = re.search(r'^PING (.+)$', message)
        if result is not None:
            # PING PONG
            with self.__lock:
                self.__queue.put('PONG ' + result.group(1))
        else:
            self.notify_observers(message)



class Sender(object):
    
    def __init__(self, local_socket, encode = 'UTF-8'):
        self.__socket = local_socket
        self.__encode = encode
    
    def send(self, message):
        self.__socket.send((message + '\n').encode(self.__encode))

