
# -*- coding: utf-8 -*-

import codecs
import os
import re
import threading
import time

from datetime import datetime

from wiz.irc.bot import IRCBOT
from wiz.util.observer import Observer
from wiz.util.observer import Observable
from wiz.util.thread import ResidentThread



class TimeMessage(object):
    def __init__(self, date, message):
        self.__date = date
        self.__message = message
    
    @property
    def date(self):
        return self.__date
    
    @property
    def date_string(self):
        return self.__date.strftime('%Y/%m/%d %H:%M')
    
    @property
    def message(self):
        return self.__message

class Timer(ResidentThread, Observable):
    def __init__(self, interval = 10):
        ResidentThread.__init__(self)
        Observable.__init__(self)
        self.__NOTIFY_INTERVAL_SEC = interval
    
    def process(self):
        self.notify_observers(datetime.now())
        time.sleep(self.__NOTIFY_INTERVAL_SEC)

class AlarmBOT(IRCBOT, Observer):
    
    def __init__(self, client):
        Observer.__init__(self)
        self.__DATE_FORMAT = '%Y/%m/%d %H:%M'
        self.__DATE_TABLE_PATH = "./alabot_date.conf"
        self.__WEEKLY_TABLE_PATH = "./alabot_weekly.conf"
        self.__lock = threading.RLock()
        self.__timer = Timer()
        self.__client = client
        self.__date_table = self.__load_date_table(self.__DATE_TABLE_PATH)
#        self.__weekly_table = self.__load_weekly_table(self.__WEEKLY_TABLE_PATH)
        self.__timer.add_observer(self)
        self.__timer.start()
    
    def on_privmsg(self, channel_name, nick_name, message):
        if re.search(r'^alabot +--close *$', message) is not None:
            with self.__lock:
                self.__timer.close()
                self.__client.close()
            return
        
        match_join = re.search(r'^alabot +--join +?#(.+)$', message)
        if match_join is not None:
            self.__client.join('#' + match_join.group(1))
            return
        
        match_ban = re.search(r'^alabot +--ban +?#(.+)$', message)
        if match_ban is not None:
            self.__client.part('#' + match_ban.group(1))
            return
        
        match_command = re.search(r'^jiho- +(.+)$', message)
        if match_command is not None:
            command = match_command.group(1)
            if command == 'help':
                self.__on_help(channel_name)
            elif command == 'list':
                self.__on_list(channel_name)
            else:
                
                match_set = re.search(r'^set +(.+?/.+?/.+?) +(.+?:.+?) +(.+)$', command)
                if match_set is not None:
                    date = match_set.group(1) + ' ' + match_set.group(2)
                    self.__on_set(channel_name, date, match_set.group(3))
                    return
                elif re.search(r'^set .+$', command) is not None:
                    self.__on_help_for_set(channel_name)
                    return
                
                match_unset = re.search(r'^unset +(.+)$', command)
                if match_unset is not None:
                    self.__on_unset(channel_name, match_unset.group(1))
                    return
                
            return
    
    def update(self, target, param = None):
        if not isinstance(target, Timer):
            super(AlarmBOT, self).update(target, param)
            return
        
        with self.__lock:
            if self.__timer.is_terminated():
                return
            
            remove_key_list = []
            for key, entry in self.__date_table.items():
                if entry.date < param:
                    for channel_name in self.__client.get_channel_name_list():
                        self.__client.privmsg(channel_name, entry.message)
                    remove_key_list.append(key)
            for remove_key in remove_key_list:
                del self.__date_table[remove_key]
            self.__save_table(self.__date_table, self.__DATE_TABLE_PATH)
    
    def __create_time_message(self, date_string, message):
        date = datetime.strptime(date_string, self.__DATE_FORMAT)
        return TimeMessage(date, message)
    
    def __load_date_table(self, source_path):
        result_table = {}
        if not os.path.exists(source_path):
            return result_table
        for line in codecs.open(source_path, 'r', 'UTF-8'):
            match_entry = re.search(r'^(.+?/.+?/.+? .+?:.+?) (.+)$', line)
            if match_entry is not None:
                date = match_entry.group(1)
                message = match_entry.group(2)
                result_table[date] = self.__create_time_message(date, message)
        return result_table
    
    def __on_help(self, channel_name):
        self.__on_help_for_set(channel_name)
        self.__on_help_for_unset(channel_name)
        self.__on_help_for_list(channel_name)
    
    def __on_help_for_list(self, channel_name):
        self.__client.privmsg(channel_name, "[一覧] jiho- list")
    
    def __on_help_for_set(self, channel_name):
        self.__client.privmsg(channel_name, "[登録] jiho- set 日付 時刻 メッセージ")
        self.__client.privmsg(channel_name, "ex) jiho- set 2015/12/25 00:00 クリスマスになりました")
#        self.__client.privmsg(channel_name, "ex) jiho- 9/11 15:30 年指定省略可 (今年として扱う)")
#        self.__client.privmsg(channel_name, "ex) jiho- 9:15 日付指定省略可 (今日として扱う)")
#        self.__client.privmsg(channel_name, "ex) jiho- 22:00")
    
    def __on_help_for_unset(self, channel_name):
        self.__client.privmsg(channel_name, "[削除] jiho- unset メッセージ")
        self.__client.privmsg(channel_name, "ex) jiho- unset クリスマスになりました (※誤爆注意！)")
    
    def __on_list(self, channel_name):
        if not self.__date_table:
            self.__client.privmsg(channel_name, "何も登録されてません")
            return
        for date, entry in sorted(self.__date_table.items(), key = lambda x: x[0]):
            self.__client.notice(channel_name, date + '  ' + entry.message)
    
    def __on_set(self, channel_name, date_string, message):
        try:
            if datetime.strptime(date_string, self.__DATE_FORMAT) < datetime.now():
                self.__client.privmsg(channel_name, "過去に生きてます： " + date_string)
                return
            
            with self.__lock:
                entry = self.__create_time_message(date_string, message)
                self.__date_table[date_string] = entry
                self.__save_table(self.__date_table, self.__DATE_TABLE_PATH)
            self.__client.privmsg(channel_name, date_string + " に以下のメッセージを出力します：")
            self.__client.privmsg(channel_name, "「" + entry.message + "」")
        except ValueError as e:
            self.__client.privmsg(channel_name, "(  ´∀｀) ＜ " + str(e))
    
    def __save_table(self, source_table, dest_path):
        with codecs.open(dest_path, 'w', 'utf_8') as dest_file:
            for key, value in source_table.items():
                dest_file.write(key + ' ' + value.message + '\n')
    
    def __on_unset(self, channel_name, message):
        remove_key_list = []
        with self.__lock:
            for key, entry in self.__date_table.items():
                if entry.message == message:
                    remove_key_list.append(key)
            for remove_key in remove_key_list:
                del self.__date_table[remove_key]
            self.__save_table(self.__date_table, self.__DATE_TABLE_PATH)
        
        if remove_key_list:
            self.__client.privmsg(channel_name, "以下のメッセージを削除しました")
            for date in remove_key_list:
                self.__client.privmsg(channel_name, "「" + message + "」 (" + date + ")")

