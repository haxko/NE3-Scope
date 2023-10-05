#!/usr/bin/env python3
import socket
import struct
import sys
import time
import argparse
import cv2
import numpy as np
from ne3 import Header, Frame

def short_to_bytes(l):
    return struct.pack("<H", l)
def int_to_bytes(i):
    return struct.pack("<Q", i)

def send_init(socket):
    data_init = bytes([0xef, 0x00, 0x04, 0x00])
    try:
        socket.sendto(data_init,(ip,port))
    except:
        pass

def send_msgs(socket, msgs):
    to_send = bytes.fromhex("02020001")
    to_send += int_to_bytes(len(msgs))
    to_send += bytes.fromhex("0000000000000000")
    to_send += bytes.fromhex("0a4b142d00000000")
    for msg in msgs:
        to_send += msg
    to_send += bytes.fromhex("0000000000000000")
    to_send = bytes([0xef, 0x02]) + short_to_bytes(len(to_send) + 4) + to_send
    try:
        socket.sendto(to_send,(ip,port))
    except:
        pass

def send_null_pkt(socket):
    try:
        socket.sendto(bytes(), (ip, 1234))
    except:
        pass

def msg_ack_img(img_number):
    return int_to_bytes(img_number) + bytes.fromhex("0100000014000000ffffffff") #@TODO: Last f's contain data in original app

def msg_req_img(img_number):
    return int_to_bytes(img_number) + bytes.fromhex("0300000010000000")
    
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

current_frame = None
last_full_image = 0
last_msg = time.time()
last_request_more = time.time()
last_null_packet = time.time()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0",36000))
s.settimeout(0.025)
send_null_pkt(s)
send_init(s)
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
            current_frame = None
            last_full_image = 0
            continue
        if last_full_image > 0 and current_frame and last_full_image == current_frame.header.img_number:
            # Timeout and last image complete - send ACK and request again
            if args.verbose:
                print("Request timed out; ACK+REQ resend")
            send_msgs(s, [msg_ack_img(current_frame.header.img_number), msg_req_img(current_frame.header.img_number + 1)])
        else:
            # Timeout and image incomplete - send request to continue transmission again
            if args.verbose:
                print("Request timed out; REQ resend")
            send_msgs(s, [])
        continue
    last_msg = time.time()
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
        last_full_image = current_frame.header.img_number
        # ACK and request next frame
        send_msgs(s, [msg_ack_img(current_frame.header.img_number), msg_req_img(current_frame.header.img_number + 1)])
    elif time.time() > last_request_more + 0.025:
        # Image not yet complete – request to continue transmission
        send_msgs(s, [])
        last_request_more = time.time()
    if time.time() > last_null_packet + 5:
        send_null_pkt(s)
        last_null_packet = time.time()
