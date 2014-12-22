
# -*- coding: utf-8 -*-

import re
import queue
import threading

from wiz.util.observer import Observer
from wiz.util.observer import Observable
from wiz.util.thread import ResidentThread



class IRCWriteThread(ResidentThread, Observer, Observable):
    
    def __init__(self):
        ResidentThread.__init__(self)
        Observer.__init__(self)
        Observable.__init__(self)
        self.__lock = threading.RLock()
        self.__sender = None
        self.__queue = queue.Queue()
    
    def put_message(self, message):
        with self.__lock:
            self.__queue.put(message)
    
    def set_sender(self, sender):
        self.__sender = sender
    
    def update(self, target, param = None):
        message = target.get_message()
        result = re.search(r'^PING (.+)$', message)
        if result is not None:
            # PING PONG
            with self.__lock:
                self.__queue.put('PONG ' + result.group(1))
        else:
            self.notify_observers(message)
    
    def _process(self):
        with self.__lock:
            while not self.__queue.empty():
                self.__sender.send(self.__queue.get())



class Sender(object):
    
    def __init__(self, local_socket):
        self.__socket = local_socket
    
    def send(self, message):
        self.__socket.send((message + '\n').encode('UTF-8'))

