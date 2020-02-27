import os
import shutil
import glob


def copyFolder(folder, dest):
    if not os.path.exists(dest):
        os.makedirs(dest)
    for i in os.listdir(folder):
        filepath = os.path.join(folder, i)
        if os.path.isdir(filepath):
            copyFolder(filepath, os.path.join(dest, filepath))
        else:
            print('{0} -> {1}'.format(filepath, dest))
            shutil.copy(filepath, dest)


def getCleanName(file):
    return os.path.basename(file).split('.')[0]


def listFile(path, extensions):
    out = []
    for i in extensions:
        out.extend(glob.glob(path + "**/*" + i, recursive=True))
    return out

def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)