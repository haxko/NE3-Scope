#!/usr/bin/env python3
import socket
import sys
import time
import argparse
import cv2
import numpy as np
from math import atan2, degrees

jpeg_header_640x360_Q5   = bytes.fromhex("ffd8ffdb004300a06e788c7864a08c828cb4aaa0bef0fffff0dcdcf0ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffdb004301aab4b4f0d2f0ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc00011080168028003011100021101031101ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffc4001f0100030101010101010101010000000000000102030405060708090a0bffc400b51100020102040403040705040400010277000102031104052131061241510761711322328108144291a1b1c109233352f0156272d10a162434e125f11718191a262728292a35363738393a434445464748494a535455565758595a636465666768696a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9faffda000c03010002110311003f00")
jpeg_header_640x360_Q10  = bytes.fromhex("ffd8ffdb00430050373c463c32504641465a55505f78c882786e6e78f5afb991c8ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffdb004301555a5a786978eb8282ebffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc00011080168028003011100021101031101ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffc4001f0100030101010101010101010000000000000102030405060708090a0bffc400b51100020102040403040705040400010277000102031104052131061241510761711322328108144291a1b1c109233352f0156272d10a162434e125f11718191a262728292a35363738393a434445464748494a535455565758595a636465666768696a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9faffda000c03010002110311003f00")
jpeg_header_640x360_Q25  = bytes.fromhex("ffd8ffdb0043002016181c1814201c1a1c24222026305034302c2c3062464a3a5074667a787266706e8090b89c8088ae8a6e70a0daa2aebec4ced0ce7c9ae2f2e0c8f0b8cacec6ffdb004301222424302a305e34345ec6847084c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6ffc00011080168028003011100021101031101ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffc4001f0100030101010101010101010000000000000102030405060708090a0bffc400b51100020102040403040705040400010277000102031104052131061241510761711322328108144291a1b1c109233352f0156272d10a162434e125f11718191a262728292a35363738393a434445464748494a535455565758595a636465666768696a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9faffda000c03010002110311003f00")
jpeg_header_640x360_Q50  = bytes.fromhex("ffd8ffdb004300100b0c0e0c0a100e0d0e1211101318281a181616183123251d283a333d3c3933383740485c4e404457453738506d51575f626768673e4d71797064785c656763ffdb0043011112121815182f1a1a2f634238426363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363ffc00011080168028003011100021101031101ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffc4001f0100030101010101010101010000000000000102030405060708090a0bffc400b51100020102040403040705040400010277000102031104052131061241510761711322328108144291a1b1c109233352f0156272d10a162434e125f11718191a262728292a35363738393a434445464748494a535455565758595a636465666768696a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9faffda000c03010002110311003f00")
jpeg_header_640x360_Q75  = bytes.fromhex("ffd8ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b0c180d0d1832211c213232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232ffc00011080168028003011100021101031101ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffc4001f0100030101010101010101010000000000000102030405060708090a0bffc400b51100020102040403040705040400010277000102031104052131061241510761711322328108144291a1b1c109233352f0156272d10a162434e125f11718191a262728292a35363738393a434445464748494a535455565758595a636465666768696a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9faffda000c03010002110311003f00")
jpeg_header_640x360_Q100 = bytes.fromhex("ffd8ffdb00430001010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101ffdb00430101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101ffc00011080168028003011100021101031101ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffc4001f0100030101010101010101010000000000000102030405060708090a0bffc400b51100020102040403040705040400010277000102031104052131061241510761711322328108144291a1b1c109233352f0156272d10a162434e125f11718191a262728292a35363738393a434445464748494a535455565758595a636465666768696a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9faffda000c03010002110311003f00")


def len_to_bytes(l):
    return bytes([l & 0xff, (l >> 8) & 0xff])
def int_to_bytes(i):
    return bytes([i & 0xff, (i >> 8) & 0xff, (i >> 16) & 0xff, (i >> 24) & 0xff, (i >> 32) & 0xff, (i >> 40) & 0xff, (i >> 48) & 0xff, (i >> 56) & 0xff])

def send_init(socket):
    data_init = bytes([0xef, 0x00, 0x04, 0x00])
    socket.sendto(data_init,(ip,port))

def send_msgs(socket, msgs):
    to_send = bytes.fromhex("02020001")
    to_send += int_to_bytes(len(msgs))
    to_send += bytes.fromhex("0000000000000000")
    to_send += bytes.fromhex("0a4b142d00000000")
    for msg in msgs:
        to_send += msg
    to_send += bytes.fromhex("0000000000000000")
    to_send = bytes([0xef, 0x02]) + len_to_bytes(len(to_send) + 4) + to_send
    socket.sendto(to_send,(ip,port))

def msg_ack_img(img_number):
    return int_to_bytes(img_number) + bytes.fromhex("0100000014000000ffffffff") #@TODO: Last f's contain data in original app

def msg_req_img(img_number):
    return int_to_bytes(img_number) + bytes.fromhex("0300000010000000")
    
def getImgHeader(img_type):
    if img_type == 5:
        return jpeg_header_640x360_Q5
    elif img_type == 10:
        return jpeg_header_640x360_Q10
    elif img_type == 25:
        return jpeg_header_640x360_Q25
    elif img_type == 50:
        return jpeg_header_640x360_Q50
    elif img_type == 75:
        return jpeg_header_640x360_Q75
    else:
        return jpeg_header_640x360_Q100


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

ip = "192.168.169.1"
port = 8800

parser = argparse.ArgumentParser(description="A Python based open source viewer for the NE3 Earpick wireless endoscope")

# Add command-line arguments
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
parser.add_argument('-r', '--rotation', action='store_true', help='Rotate image')

args = parser.parse_args()

current_packet = {}
current_img_number = 1
current_angle = 0
last_full_image = 0
last_msg = time.time()
last_request_more = time.time()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0",36000))
s.settimeout(0.1)
send_init(s)
img_number = 0
while True:
    try:
        data, addr = s.recvfrom(1500) #Try to receive data
    except TimeoutError:
        if time.time() > last_msg + 120: # Connection probably lost
            print("Connection lost")
            sys.exit(1)
        if time.time() > last_msg + 0.5: # Reconnect
            if args.verbose:
                print("Request timed out; Reconnecting")
            send_init(s)
            current_img_number = 1
            last_full_image = 0
            current_packet = {}
            continue
        if last_full_image > 0 and last_full_image == current_img_number:
            # Timeout and last image complete - send ACK and request again
            if args.verbose:
                print("Request timed out; ACK+REQ resend")
            send_msgs(s, [msg_ack_img(current_img_number), msg_req_img(current_img_number + 1)])
        else:
            # Timeout and image incomplete - send request to continue transmission again
            if args.verbose:
                print("Request timed out; REQ resend")
            send_msgs(s, [])
        continue
    last_msg = time.time()
    header = data[:56]
    length = header[2] | (header[3] << 8)
    packet_number = int(header[32]) + int(header[33] << 8) + int(header[34] << 16) + int(header[35] << 24)
    packet_count = int(header[36]) + int(header[37] << 8) + int(header[38] << 16) + int(header[39] << 24)
    img_number = int(header[8]) + int(header[9] << 8) + int(header[10] << 16) + int(header[11] << 24) + int(header[12] << 32) + int(header[13] << 40) + int(header[14] << 48) + int(header[15] << 56)
    d = data[56:]
    if img_number > current_img_number:
        #Started receiving new image. Clear buffer.
        current_img_number = img_number
        current_packet = {}
    if img_number < current_img_number:
        #Received older image than displayed - discard
        continue
    current_packet[packet_number] = d[:1024]
    if packet_number == 0:
        a = d[1024:]
        current_angle = atan2(int(a[:5].decode()), int(a[6:].decode()))
        current_angle = degrees(current_angle)
    if len(current_packet) == packet_count:
        #Image RX complete
        if args.verbose:
            print("img_number:", img_number, file=sys.stderr)
        img_type = header[48]
        img = getImgHeader(img_type)
        for i in range(packet_count):
            img += current_packet[i]
        nparr = np.frombuffer(img, dtype=np.uint8)
        img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if args.rotation:
            img2_cv = rotate_image(img_cv, current_angle * -1 - 90)
        else:
            img2_cv = img_cv
        cv2.imshow('image', img2_cv)
        cv2.waitKey(2)
        last_full_image = img_number
        # ACK and request next frame
        send_msgs(s, [msg_ack_img(current_img_number), msg_req_img(current_img_number + 1)])
    if len(current_packet) < packet_count and time.time() > last_request_more + 0.025:
        # Image not yet complete – request to continue transmission
        send_msgs(s, [])
        last_request_more = time.time()
