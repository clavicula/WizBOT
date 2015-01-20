
# -*- coding: utf-8 -*-

import threading



class ClosableThread(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.__lock = threading.RLock()
        self.__terminated = False
    
    def close(self):
        with self.__lock:
            self.__terminated = True
    
    def is_terminated(self):
        with self.__lock:
            return self.__terminated



class ResidentThread(ClosableThread):
    
    def __init__(self):
        ClosableThread.__init__(self)
    
    def process(self):
        raise NotImplementedError
    
    def run(self):
        while not self.is_terminated():
            self.process()

