
# -*- coding: utf-8 -*-

import re

from contextlib import closing

from wiz.irc.bot import IRCBOT
from wiz.irc.client import IRCClient



SERVER_HOST   = "www.foo.com"

SERVER_PORT   = 1234

BOT_NICK_NAME = "WizBOT"

CHANNEL_LIST  = ["#my-channel", "#your-channel"]





class PrintBOT(IRCBOT):
    
    def __init__(self):
        IRCBOT.__init__(self)
    
    def on_privmsg(self, message):
        print(message)



class CloseBOT(IRCBOT):
    
    def __init__(self, client):
        IRCBOT.__init__(self)
        self.__client = client
    
    def on_privmsg(self, channel_name, message):
        if re.search(r'bot +--close', message) is not None:
            self.__client.close()



class EchoBOT(IRCBOT):
    
    def __init__(self, client):
        IRCBOT.__init__(self)
        self.__client = client
    
    def on_privmsg(self, channel_name, message):
        self.__client.privmsg(channel_name, message)





def main():
    # Create IRC client
    with closing(IRCClient()) as client:
        
        # Register BOT
        bot = EchoBOT(client)
        client.add_message_listener(PrivmsgListener(bot))
        
        # Connect and login to server
        client.connect(SERVER_HOST, SERVER_PORT, BOT_NICK_NAME)
        
        # Join channel
        for channel_name in CHANNEL_LIST:
            client.join(channel_name)
        
        # Have a nice BOT ;-)
        while not client.is_closed():
            pass





if __name__ == '__main__':
    main()

