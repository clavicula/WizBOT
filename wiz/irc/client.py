
# -*- coding: utf-8 -*-

import re
import queue
import socket
import threading

from wiz.util.observer import Observer

from wiz.irc.__irc_read_thread import IRCReadThread
from wiz.irc.__irc_read_thread import Receiver
from wiz.irc.__irc_write_thread import IRCWriteThread
from wiz.irc.__irc_write_thread import Sender
from wiz.irc.__message_type import MessageType



class IRCClient(Observer):
    
    def __init__(self):
        Observer.__init__(self)
        self.__core = self._create_socket()
        self.__closed = False
        self.__logged_in = False
        self.__read_thread = IRCReadThread()
        self.__write_thread = IRCWriteThread()
        self.__write_buffer = queue.Queue()
        
        self.__read_thread.set_receiver(Receiver(self.__core))
        self.__read_thread.add_observer(self.__write_thread)
        self.__write_thread.set_sender(Sender(self.__core))
        self.__write_thread.add_observer(self)
    
    def add_message_listener(self, listener):
        self.__write_thread.add_observer(listener)
    
    def close(self):
        self.__read_thread.close()
        self.__write_thread.close()
        self.__core.close()
        self.__closed = True
    
    def connect(self, host, port, nick_name, login_name = 'WizBOT', label = 'Wiz BOT framework'):
        self.__core.connect((host, port))
        self.__read_thread.start()
        self.__write_thread.start()
        
        self.__write_thread.put_message('USER ' + login_name + ' ' + host + ' ignore ' + label)
        self.__write_thread.put_message('NICK ' + nick_name)
        while not self.__logged_in:
            # Waiting for logged in
            pass
    
    def is_closed(self):
        return self.__closed
    
    def join(self, channel_name):
        self.__write_thread.put_message('JOIN ' + channel_name)
    
    def privmsg(self, channel_name, message):
        self.__write_thread.put_message('PRIVMSG ' + channel_name + ' ' + message)
    
    def update(self, target, param = None):
        if re.search(r'(.+)? 001 (.+)$', param) is not None:
            # Welcome message
            self.__logged_in = True
    
    def _create_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)



class MessageListener(Observer):
    
    def __init__(self):
        Observer.__init__(self)
    
    def on_receive(self, message):
        pass
    
    def update(self, target, param = None):
        self.on_receive(param)

