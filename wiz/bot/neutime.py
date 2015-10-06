
# -*- coding: utf-8 -*-

import math
import re
import time

from wiz.irc.bot import IRCBOT



class NeuTimeBOT(IRCBOT):
    
    def __init__(self, client):
        self.__client = client
        self.__start_time = 0;
    
    def on_privmsg(self, channel_name, nick_name, message):
        if re.search(r'^ *neutimebot +--close *$', message) is not None:
            self.__client.close()
            return
        
        if re.search(r'-------- ゲーム開始 --------', message) is not None:
            if nick_name == 'NeuBot':
                self.__start_time = time.time()
                return
        
        if re.search(r'youの勝ち！！', message) is not None:
            if nick_name == 'NeuBot':
                self.__print_time(channel_name)
                return
        
        if re.search(r'youは死んだ。', message) is not None:
            if nick_name == 'NeuBot':
                self.__print_time(channel_name)
                return
    
    def __print_time(self, channel_name):
        result_time = time.time() - self.__start_time
        self.__start_time = 0
        self.__client.privmsg(channel_name, "result time: %.2fsec" % result_time)

