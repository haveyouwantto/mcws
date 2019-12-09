import glob
import json
import os
import time
import shutil

import xbox

import avatar_downloader as avatar
import mcws
import fileutils


class ChatLogger:
    def __init__(self, ws):
        self.ws = ws
        self.players = []
        for i in glob.glob('cache/avatar/*.png'):
            self.players.append(fileutils.getCleanName(i))

    def authenticate(self):
        account_details = open('login.txt', 'r').read().split(':')
        self.account = xbox.client.authenticate(login=account_details[0], password=account_details[1])

    async def getHost(self):
        await self.ws.send(mcws.cmd('testfor @s'))
        msg = await self.ws.recv()
        print(msg)
        self.host = json.loads(msg)['body']['victim'][0]
        self.chatmsg = {
            'time': time.time(),
            'host_name': self.host,
            'messages': []
        }
        print(self.chatmsg)

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

        if sender not in self.players:
            self.players.append(sender)
            avatar.download_avatar(sender)

        if ('Receiver' in prop):
            info['receiver'] = prop['Receiver']

        self.chatmsg['messages'].append(info)
        print(info)

    def close(self):
        localTime = time.localtime(float(self.chatmsg['time']))
        date = time.strftime('%Y-%m-%d_%H-%M-%S', localTime)

        out = 'chat_logs/' + date + '/'

        if not os.path.exists(out):
            os.makedirs(out)
            os.makedirs(os.path.join(out, 'avatar/'))

        for file in os.listdir('template/'):
            shutil.copyfile('template/' + file, out + file)

        for name in self.players:
            shutil.copyfile('cache/avatar/' + name + '.png', os.path.join(out, 'avatar/', name + '.png'))

        outjson = json.dumps(self.chatmsg)
        datajs = open(out + 'data.js', 'w', encoding='utf-8-sig')
        datajs.write('let chat=' + outjson + ';')
        datajs.write('init(chat);')
        datajs.close()