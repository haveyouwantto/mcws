import struct
import argparse
import gzip


def read(file):
    if file.endswith('.mcz'):
        f = gzip.open(file, 'rb')
    else:
        f = open(file, 'rb')
    notes = []
    f.seek(4, 0)
    version = struct.unpack('<h', f.read(2))[0]
    multiplier = struct.unpack('<f', f.read(4))[0]
    length = struct.unpack('<i', f.read(4))[0]
    for i in range(length):
        tick = struct.unpack('<h', f.read(2))[0]
        inst = f.read(1)[0]
        pitch = f.read(1)[0]
        notes.append({
            'time': tick,
            'inst': inst,
            'pitch': pitch
        })
    f.close()
    return {
        'version': version,
        'multiplier': multiplier,
        'notes': notes
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str,
                        help='File')
    args = parser.parse_args()

    print(read(args.file))
