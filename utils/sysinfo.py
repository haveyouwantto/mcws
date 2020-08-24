import sys
import platform


def sysinfo():
    return {
        'python': sys.version,
        'platform': platform.platform(),
        'hostname': platform.node(),
        'arch': platform.machine()
    }
