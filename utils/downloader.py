import urllib.request
import os

image = ('image/png', 'image/jpeg', 'image/bmp', 'image/webp', 'image/gif')
midi= ('audio/mid','audio/midi')

def download(url, name, mime):
    try:
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://'+url
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        if response.info()['Content-Type'] not in mime:
            return (1,response.info()['Content-Type'])
        filename = "cache/" + name
        if (response.getcode() == 200):
            with open(filename, "wb") as f:
                f.write(response.read())  # 将内容写入图片
            return (0,)
    except:
        return (-1,)


def download_image(url):
    return download(url,'img' ,image)


def download_midi(url):
    return download(url,'midi', midi)
