# NE3-Scope

A Python based open source viewer for the NE3 Earpick wireless endoscope

## Webcam mode

Webcam mode is only available on unix systems. Ensure v4l2loopback is installed and loaded (v4l2loopback-dkms on arch). Ensure the module is loaded and check the device name (v4l2-ctl --list-devices).
Call the script with -w /dev/video1 (or whatever your loopback device was assigned). Keep in mind your user must be able to write to the device file. To use webcam mode ensure v4l2 is installed (pip install v4l2).
