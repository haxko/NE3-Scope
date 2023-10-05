import struct
import dataclasses
from math import atan2, degrees

class Header:
    def __init__(self, packet):
        data = packet[:56]
        (self.length, self.img_number, img_number2, self.packet_number, self.packet_count, self.img_size, self.img_width, self.img_height, self.img_quality) = struct.unpack("<xxHxxxxQQxxxxxxxxIIIHHBxxxxxxx", data)


class Frame:
    def __init__(self, header):
        self.header = header
        self.chunks = {}
        self.angle = 0

    def add(self, data):
        header = Header(data)
        d = data[56:]
        if header.packet_number == 0:
            a = d[1024:]
            x = int(a[:5].decode())
            y = int(a[6:].decode())
            if x == 0 and y == 1024:
                self.angle = 90
            else:
                angle = atan2(x, y)
                self.angle = degrees(angle)
        self.chunks[header.packet_number] = d[:1024]

    def complete(self):
        return len(self.chunks) == self.header.packet_count

    def data(self):
        data = Frame.assemble_jpeg_header(self.header.img_quality, self.header.img_height, self.header.img_width)
        for i in range(self.header.packet_count):
            data += self.chunks[i]
        data += bytes.fromhex("ffd9") # end of image
        return data

    @staticmethod
    def assemble_jpeg_header(q, h, w):
        out = bytes()
        out += bytes.fromhex("ffd8") # start of image
        # quantization tables (luminance + chrominance)
        if q == 5:
            out += bytes.fromhex("ffdb004300a06e788c7864a08c828cb4aaa0bef0fffff0dcdcf0ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
            out += bytes.fromhex("ffdb004301aab4b4f0d2f0ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
        elif q == 10:
            out += bytes.fromhex("ffdb00430050373c463c32504641465a55505f78c882786e6e78f5afb991c8ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
            out += bytes.fromhex("ffdb004301555a5a786978eb8282ebffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
        elif q == 25:
            out += bytes.fromhex("ffdb0043002016181c1814201c1a1c24222026305034302c2c3062464a3a5074667a787266706e8090b89c8088ae8a6e70a0daa2aebec4ced0ce7c9ae2f2e0c8f0b8cacec6")
            out += bytes.fromhex("ffdb004301222424302a305e34345ec6847084c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6")
        elif q == 50:
            out += bytes.fromhex("ffdb004300100b0c0e0c0a100e0d0e1211101318281a181616183123251d283a333d3c3933383740485c4e404457453738506d51575f626768673e4d71797064785c656763")
            out += bytes.fromhex("ffdb0043011112121815182f1a1a2f634238426363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363")
        elif q == 75:
            out += bytes.fromhex("ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432")
            out += bytes.fromhex("ffdb0043010909090c0b0c180d0d1832211c213232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232")
        else: # q: 100
            out += bytes.fromhex("ffdb00430001010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101")
            out += bytes.fromhex("ffdb00430101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101")
        # start of frame
        out += bytes.fromhex("ffc0001108")
        out += struct.pack(">hh", h, w)
        out += bytes.fromhex("03011100021101031101")
        # huffman tables
        out += bytes.fromhex("ffc4001f0000010501010101010100000000000000000102030405060708090a0b")
        out += bytes.fromhex("ffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9fa")
        out += bytes.fromhex("ffc4001f0100030101010101010101010000000000000102030405060708090a0b")
        out += bytes.fromhex("ffc400b51100020102040403040705040400010277000102031104052131061241510761711322328108144291a1b1c109233352f0156272d10a162434e125f11718191a262728292a35363738393a434445464748494a535455565758595a636465666768696a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9fa")
        # start of scan
        out += bytes.fromhex("ffda000c03010002110311003f00")
        return out
