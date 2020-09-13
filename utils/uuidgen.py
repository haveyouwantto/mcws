import uuid
import time
from threading import Lock

_id = 1
lock = Lock()

'''
def gen():
    return str(uuid.uuid4())
'''


def gen():
    global _id
    global lock
    lock.acquire()
    v0 = (_id >> 96) & 0xffffffff
    v1 = (_id >> 80) & 0xffff
    v2 = (_id >> 64) & 0xffff
    v3 = (_id >> 48) & 0xffff
    v4 = _id & 0xffffffffffff
    _id += 1
    lock.release()
    return '{0:08x}-{1:04x}-{2:04x}-{3:04x}-{4:012x}'.format(v0, v1, v2, v3, v4)
