import xboxapi
import requests
import os


def download_avatar(username, size=56, format='png'):
    if (format != 'png' and format != 'jpg'):
        raise Exception('Format must be either png or jpg')
    print('Trying download avatar of ' + username)
    url = xboxapi.getUserData(username)['DisplayImage']['Href'] + "&h=" + str(size) + "&w=" + str(size)
    url = url.replace('format=png', 'format=' + format)
    r = requests.get(url, stream=True)
    print('server returned code ' + str(r.status_code))  # 返回状态码
    if r.status_code == 200:
        if not os.path.exists('cache/avatar'):
            os.makedirs('cache/avatar')
        open('cache/avatar/' + username + '.' + format, 'wb').write(r.content)
    del r
    print('Downloaded avatar of ' + username)
