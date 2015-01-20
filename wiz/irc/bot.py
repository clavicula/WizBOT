
# -*- coding: utf-8 -*-

import re

from wiz.util.observer import Observer



class MessageListener(object):
    
    def on_privmsg(self, channel_name, message):
        raise NotImplementedError



class IRCBOT(MessageListener, Observer):
    
    def __init__(self):
        pass
    
    def on_receive(self, message):
        word_list = message.split()
        if len(word_list) < 2:
           return
        
        if word_list[1] == 'PRIVMSG':
            channel_name = word_list[2]
            match = re.search(r'.*?:(.+?)!.+? PRIVMSG ' + channel_name + ' :(.+)$', message)
            if match is not None:
                self.on_privmsg(channel_name, match.group(1), match.group(2))
    
    def update(self, target, param = None):
        self.on_receive(param)

