#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket

server = ("127.0.0.1", 1661)
bufferSize = 1024

msgToSend = []

# CCT Reset
#  msgToSend.append(b"\x78\x87\x02\x62\x26\x89")
# HSI: Yellow/green
msgToSend.append(b"\x78\x86\x04\x4b\x00\x60\x49\xf6")
# HSI: Blueish
#  msgToSend.append(b"\x78\x86\x04\x16\x00\x11\x49\x72")
# HSI: Pink
#  msgToSend.append(b"\x78\x86\x04\x16\x00\x2c\x49\x8d")
# HSI: Test
msgToSend.append(b"\x78\x86\x04\x00\x00\xff\x49\xff")

#  def creepyIncrement(value: bytes, inc):
#      """
#      Return an array of incremented bytes
#      """
#      allValues = []
#      length = len(value)
#      number = int.from_bytes(value, 'big')
#      for count in range(0, inc):
#          number = number + count
#          print("%s: %s" % (count, number.to_bytes(length, 'big')))
#          allValues.append(number.to_bytes(length, 'big'))
#      return allValues

#  def byteArrayInc(value, inc):
#      allValues = []
#      for count in range(0, inc):
#          print("%s: %s" % (count, value + bytes([count])))
#          allValues.append(value + bytes([count]))
#      return allValues

#  for msg in creepyIncrement(b"\x78\x86\x04\x16\x00\x2c\x49\x00", 255):
#      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#      s.sendto(msg, server)

#  for msg in byteArrayInc(b"\x78\x86\x04\x16\x00\x2c\x49", 255):
#      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#      s.sendto(msg, server)

for msg in msgToSend:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(msg, server)
