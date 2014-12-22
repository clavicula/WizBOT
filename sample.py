
# -*- coding: utf-8 -*-

import re

from contextlib import closing

from wiz.irc.client import IRCClient
from wiz.irc.client import MessageListener



SERVER_HOST   = "www.foo.com"

SERVER_PORT   = 1234

BOT_NICK_NAME = "WizBOT"

CHANNEL_LIST  = ["#my-channel", "#your-channel"]





class PrintBOT(MessageListener):
    
    def __init__(self):
        MessageListener.__init__(self)
    
    def on_receive(self, message):
        print(message)



class CloseBOT(MessageListener):
    
    def __init__(self, client):
        MessageListener.__init__(self)
        self._client = client
    
    def on_receive(self, message):
        if re.search(r'bot +--close', message) is not None:
            client.close()



class EchoBOT(MessageListener):
    
    def __init__(self, client):
        MessageListener.__init__(self)
        self._client = client
    
    def on_receive(self, message):
        word_list = message.split()
        if word_list[1] == 'PRIVMSG':
            channel_name = word_list[2]
            value = re.search(r'.+' + channel_name + ' :(.+)$', message).group(1)
            client.privmsg(channel_name, value)





if __name__ == '__main__':
    # Create IRC client
    with closing(IRCClient()) as client:
        
        # Register BOT
        client.add_message_listener(PrintBOT())
        client.add_message_listener(CloseBOT(client))
        client.add_message_listener(EchoBOT(client))
        
        # Connect and login to server
        client.connect(SERVER_HOST, SERVER_PORT, BOT_NICK_NAME)
        
        # Join channel
        for channel_name in CHANNEL_LIST:
            client.join(channel_name)
        
        # Have a nice BOT ;-)
        while not client.is_closed():
            pass

