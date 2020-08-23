# deprecated

import requests
import xbox
import os

def download_avatar(username, size=56, format='png'):
    if (format != 'png' and format != 'jpg'):
        raise Exception('Format must be either png or jpg')
    print('Trying download avatar of ' + username)
    profile = xbox.GamerProfile.from_gamertag(username)
    url = profile.gamerpic + "&h=" + str(size) + "&w=" + str(size)
    r = requests.get(url, stream=True)
    print('server returned code ' + str(r.status_code))  # 返回状态码
    if r.status_code == 200:
        if not os.path.exists('../files/cache/avatar'):
            os.makedirs('cache/avatar')
        open('cache/avatar/' + username + '.' + format, 'wb').write(r.content)
    del r
    print('Downloaded avatar of ' + username)
