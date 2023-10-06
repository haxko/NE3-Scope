import struct
from math import atan2, degrees

class Header:
    def __init__(self, packet):
        data = packet[:4]
        self.frame_number, self.flags, self.chunk_number, self.flags2 = struct.unpack("BBBB", data)

class Frame:
    def __init__(self, header):
        self.header = header
        self.chunks = {}
        self._complete = False

    def add(self, data):
        header = Header(data)
        d = data[4:]
        if header.flags & 1:
            print(d[-5:].hex())
            d = d[:-5]
        self.chunks[header.chunk_number-1] = d
        if header.flags & 1 and len(self.chunks) == header.chunk_number:
            self._complete = True

    def complete(self):
        return self._complete

    def data(self):
        data = bytes()
        for i in range(len(self.chunks)):
            data += self.chunks[i]
        return data

