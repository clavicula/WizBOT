
# -*- coding: utf-8 -*-

import codecs
import os
import re

from wiz.irc.bot import IRCBOT



class SignalBOT(IRCBOT):
    
    def __init__(self, client):
        self.__TABLE_PATH = "./signal.conf"
        self.__client = client
        self.__table = self.__load_table(self.__TABLE_PATH)
    
    def on_privmsg(self, channel_name, nick_name, message):
        if re.search(r'^ *jiho- +--close *$', message) is not None:
            self.__client.close()
            return
        
        if re.search(r'^ *jiho- +help *$', message) is not None:
            self.__on_help(channel_name)
            return
        
        if re.search(r'^ *jiho- +list *$', message) is not None:
            self.__on_listup(channel_name)
            return
        
        if re.search(r'^ *jiho- +set +(.+?) +(.+)$', message) is not None:
            self.__on_set(channel_name, match_set.group(1), match_set.group(2))
            return
        
        if re.search(r'^ *jiho- +unset +(.+)$', message) is not None:
            self.__on_unset(channel_name, match_unset.group(1))
            return
        
        self.__on_keyword(channel_name, message)
    
    def __load_table(self, source_path):
        result_table = {}
        if not os.path.exists(source_path):
            return result_table
        for line in codecs.open(source_path, 'r', 'utf_8'):
            entry = re.search(r'^(.+?) (.+)$', line)
            if entry is not None:
                result_table[entry.group(1)] = entry.group(2)
        return result_table
    
    def __on_keyword(self, channel_name, message):
        for key, value in self.__table.items():
            if re.match(key + '$', message) is not None:
                self.__client.privmsg(channel_name, value)
                return
    
    def __on_listup(self, channel_name, target = ''):
        buf = []
        total_character = 0
        for key in sorted(self.__table.keys()):
            if target:
                if re.search(target, key) is None:
                    continue
            
            buf.append(key)
            total_character += len(key)
            if (total_character > 255):
                self.__client.privmsg(channel_name, ' / '.join(buf))
                buf = []
                total_character = 0
        self.__client.privmsg(channel_name, ' / '.join(buf))
    
    def __on_set(self, channel_name, key, value):
        if key == 'libotls' or key == 'set' or key == 'unset' or key == 'find':
            self.__client.privmsg(channel_name, "スルーします")
            return
        if self.has_key(key):
            self.__client.privmsg(channel_name, "登録済みです -> " + key)
            return
        if len(self.__table) >= 127:
            self.__client.privmsg(channel_name, "登録数の上限を超えています (127words)")
            return
        self.__table[key] = value
        self.__save_table(self.__table, self.__TABLE_PATH)
        self.__client.privmsg(channel_name, "登録しました -> " + key)
    
    def __on_unset(self, channel_name, key):
        for k, v in self.__table.items():
            if re.match(k + '$', key) is not None:
                del self.__table[k]
                self.__client.privmsg(channel_name, "削除しました -> " + key)
                self.__save_table(self.__table, self.__TABLE_PATH)
                return
        self.__client.privmsg(channel_name, "登録されていません -> " + key)
    
    def __save_table(self, source_table, dest_path):
        with codecs.open(dest_path, 'w', 'utf_8') as dest_file:
            for key, value in source_table.items():
                dest_file.write(key + ' ' + value + '\n')

