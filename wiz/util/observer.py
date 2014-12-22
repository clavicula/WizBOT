
# -*- coding: utf-8 -*-

import threading



class Observer(object):
    
    def __init__(self):
        pass
    
    def update(self, target, param = None):
        pass



class Observable(object):
    
    def __init__(self):
        self.__observer_list = []
        self.__lock = threading.RLock()
    
    def add_observer(self, observer):
        with self.__lock:
            if not observer in self.__observer_list:
                self.__observer_list.append(observer)
    
    def notify_observers(self, param=None):
        with self.__lock:
            for observer in self.__observer_list:
                observer.update(self, param)
    
    def remove_observer(self, observer):
        with self.__lock:
            try:
                self.__observer_list.remove(observer)
            except ValueError:
                pass

