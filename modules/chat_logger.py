import glob
import json
import os
import shutil
import time

from utils import fileutils, message_utils
from static import ref_strings

from modules.__init__ import BaseModule

import_avatar = True
try:
    from deprecated import avatardownload as avatar
except ImportError:
    import_avatar = False
    print(ref_strings.import_error.avatardownload)


# import xbox

class ChatLogger(BaseModule):
    def __init__(self, ws):
        BaseModule.__init__(self, ws)
        self.players = []
        self.history_players = []
        for i in glob.glob('files/cache/avatar/*.png'):
            self.history_players.append(fileutils.getCleanName(i))
        self.config = {}
        self.default_config = {
            'downloadAvatar': False
        }

    async def getHost(self):
        await self.ws.send(message_utils.autocmd('getlocalplayername'))
        msg = await self.ws.recv()
        self.host = json.loads(msg)['body']['localplayername']
        self.chatmsg = {
            'time': time.time(),
            'host_name': self.host,
            'messages': []
        }
        return self.host

    def log(self, parsed):
        ts = time.time()
        type = parsed['body']['eventName']
        prop = parsed['body']['properties']
        sender = prop['Sender']
        message = prop['Message']
        sending_method = prop['MessageType']
        is_host = (self.host == sender)

        info = {
            'time': ts,
            'type': type,
            'sender': sender,
            'message': message,
            'is_host': is_host,
            'sending_method': sending_method,
            'receiver': None
        }

        if sender not in self.history_players:
            self.history_players.append(sender)
            if import_avatar and self.config['downloadAvatar']:
                avatar.download_avatar(sender)

        if sender not in self.players:
            self.players.append(sender)

        if ('Receiver' in prop):
            info['receiver'] = prop['Receiver']

        self.chatmsg['messages'].append(info)
        message_utils.log('<{0}> {1}'.format(sender, message))

    def close(self):
        if self.chatmsg['messages'] != []:
            localTime = time.localtime(float(self.chatmsg['time']))
            date = time.strftime('%Y-%m-%d_%H-%M-%S', localTime)

            out = os.path.join('files/chat_logs/', date)

            if not os.path.exists(out):
                os.makedirs(out)
                os.makedirs(os.path.join(out, 'avatar/'))

            for file in os.listdir('../files/template/'):
                shutil.copyfile('template/' + file, out + file)

            for name in self.players:
                try:
                    shutil.copyfile('files/cache/avatar/' + name + '.png',
                                os.path.join(out, 'avatar/', name + '.png'))
                except:
                    message_utils.warning('player ' + name + ' not found')

            outjson = json.dumps(self.chatmsg)
            datajs = open(out + 'data.js', 'w', encoding='utf-8-sig')
            datajs.write('let chat=' + outjson + ';')
            datajs.write('init(chat);')
            datajs.close()


'''
print('加载中...')
with open('login.txt', 'r') as ld:
    account_details = ld.read().split(':')
    account = xbox.client.authenticate(login=account_details[0], password=account_details[1])'''
