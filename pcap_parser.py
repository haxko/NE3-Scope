#!/usr/bin/env python3
import sys
import argparse
import cv2
import numpy as np
from scapy.all import *
from ne3 import Header, Frame


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
parser.add_argument("filename", help="path to pacp")

args = parser.parse_args()

current_frame = None
current_angle = 0

for packet in rdpcap(args.filename):
    if IP not in packet:
        continue
    if packet[IP].src != ip:
        continue
    if UDP not in packet:
        continue
    data = bytes(packet[UDP].payload)
    if data[0] != 0x93:
        continue
    if data[1] == 0x04:
        # TODO ctlmsg
        continue
    if data[1] != 0x01:
        continue
    header = Header(data)
    if not current_frame:
        current_frame = Frame(header)
    if header.img_number > current_frame.header.img_number:
        #Started receiving new image. Clear buffer.
        current_frame = Frame(header)
    if header.img_number < current_frame.header.img_number:
        #Received older image than displayed - discard
        continue
    current_frame.add(data)
    if current_frame.complete():
        #Image RX complete
        if args.verbose:
            print("img_number:", current_frame.header.img_number, file=sys.stderr)
        nparr = np.frombuffer(current_frame.data(), dtype=np.uint8)
        img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if args.rotation:
            img2_cv = rotate_image(img_cv, current_frame.angle * -1 - 90)
        else:
            img2_cv = img_cv
        cv2.imshow('image', img2_cv)
        cv2.waitKey(2)
