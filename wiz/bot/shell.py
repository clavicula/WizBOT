
# -*- coding: utf-8 -*-

import pexpect
import re
import time

from wiz.irc.bot import IRCBOT



class ShellBOT(IRCBOT):
    
    def __init__(self, client):
        self.__client = client
        self.__core = pexpect.spawn('/bin/bash')
    
    def on_privmsg(self, channel_name, nick_name, message):
        if re.search(r'^ *shbot +--close *$', message) is not None:
            self.__client.close()
            return
        
        if message == 'sh':
            self.__on_shell(channel_name, '')
            return
        
        match_sh = re.search(r'^sh +(.+)$', message)
        if match_sh is not None:
            self.__on_shell(channel_name, match_sh.group(1))
            return
    
    def __on_shell(self, channel_name, command):
        self.__core.expect(r'.*$')  # clear buffer
        self.__core.sendline(command)
        time.sleep(0.1)
        
        self.__core.readline()
        self.__core.expect(r'.*$')
        response = self.__core.after.decode('UTF-8')
        
        if not response:
            self.__client.privmsg(channel_name, "time out?")
            return
        
        result_list = response.split('\r\n')
        for result in result_list:
            if not re.search(r'^\[.*@.*\].+$', result):
                self.__client.privmsg(channel_name, result)

