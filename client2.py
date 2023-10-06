#!/usr/bin/env python3
import socket
import struct
import sys
import time
import argparse
import cv2
import numpy as np
from math import atan2, degrees
import json
from ne7 import Header, Frame

broadcast_ip = "192.168.1.255"
ip = None

last_frame_number = None
current_frame = None
current_angle = 0

def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def send_discovery_pkt(socket):
    try:
        socket.sendto(bytes([0x66, 0x39, 0x01, 0x01]), (broadcast_ip, 58090))
        socket.sendto(bytes([0x66, 0x39, 0x01, 0x01]), (broadcast_ip, 46526))
    except:
        pass

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(("0.0.0.0",36123))
s.settimeout(1.0)

send_discovery_pkt(s)

try:
    data, addr = s.recvfrom(1500) #Try to receive data
except TimeoutError:
    print("no response to broadcast", file=sys.stderr) 
    sys.exit(1)

ip, _ = addr
print(json.loads(data.decode()))

s.settimeout(0.25)

s.sendto(bytes([0x86, 0x06, 0x01]), (ip, 52219))
s.sendto(bytes([0x20, 0x36]), (ip, 44506))

while True:
    data, addr = s.recvfrom(1500) #Try to receive data
    if addr[1] == 44506:
        header = Header(data)
        if header.frame_number != last_frame_number:
            current_frame = Frame(header)
            last_frame_number = header.frame_number
        current_frame.add(data)
    elif addr[1] == 52219:
        x, y, z, a = struct.unpack(">BxBxBxxxxxxxxxxxxxHxxxx", data)
        current_angle = a
        if current_frame.complete():
            nparr = np.frombuffer(current_frame.data(), dtype=np.uint8)
            img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img_cv = cv2.resize(img_cv, None, fx=2.0, fy=2.0)
            img_cv = rotate_image(img_cv, -current_angle)
            cv2.imshow('image', img_cv)
            cv2.waitKey(2)
        print(x, y, z, a)
