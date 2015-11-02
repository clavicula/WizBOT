
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
        if re.search(r'^shbot +--close *$', message) is not None:
            self.__client.close()
            return
        
        match_join = re.search(r'^shbot +--join +?#(.+)$', message)
        if match_join is not None:
            self.__client.join('#' + match_join.group(1))
            return
        
        match_ban = re.search(r'^shbot +--ban +?#(.+)$', message)
        if match_ban is not None:
            self.__client.part('#' + match_ban.group(1))
            return
        
        if message == 'sh':
            self.__on_shell(channel_name, '')
            return
        
        match_sh = re.search(r'^sh +(.+)$', message)
        if match_sh is not None:
            command = match_sh.group(1)
            if command == 'help':
                self.__on_help(channel_name)
            else:
                self.__on_shell(channel_name, command)
            return
        
        match_shctrl = re.search(r'^shctrl +(.+)$', message)
        if match_shctrl is not None:
            command = match_shctrl.group(1).lower()
            if command in { 'c' }:
                self.__on_control_key(channel_name, command)
            else:
                self.__client.privmsg(channel_name, "unsupported key : " + command)
            return
        
        match_shkey = re.search(r'^shkey +(.+)$', message)
        if match_shkey is not None:
            command = match_shkey.group(1).lower()
            if command in { 'q' }:
                self.__on_key(channel_name, command)
            else:
                self.__client.privmsg(channel_name, "unsupported key : " + command)
            return
    
    def __on_control_key(self, channel_name, command):
        self.__core.expect(r'.*$')  # clear buffer
        self.__core.sendcontrol(command)
        self.__show_response(channel_name)
    
    def __on_help(self, channel_name):
        self.__client.privmsg(channel_name, "sh [command] : send shell command (ex. sh ls -l)")
        self.__client.privmsg(channel_name, "sh : simulate the enter key press")
        self.__client.privmsg(channel_name, "shctrl [key] : simulate the Ctrl+[key] press (ex. shctrl c)")
    
    def __on_key(self, channel_name, command):
        # it doesn't work well...
        self.__core.expect(r'.*$')  # clear buffer
        self.__core.send(command)
        self.__on_shell(channel_name, '')
    
    def __on_shell(self, channel_name, command):
        self.__core.expect(r'.*$')  # clear buffer
        self.__core.sendline(command)
        self.__show_response(channel_name)
    
    def __show_response(self, channel_name):
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
    

