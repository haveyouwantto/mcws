from threading import Lock

id = 1

lock = Lock()


def gen():
    global id
    global lock
    v0 = (id >> 96) & 0xffffffff
    v1 = (id >> 80) & 0xffff
    v2 = (id >> 64) & 0xffff
    v3 = (id >> 48) & 0xffff
    v4 = id & 0xffffffffffff
    lock.acquire()
    id += 1
    lock.release()
    return ('{0:08x}-{1:04x}-{2:04x}-{3:04x}-{4:012x}'.format(v0, v1, v2, v3, v4))
