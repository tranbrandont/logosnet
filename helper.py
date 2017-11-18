#!/usr/bin/python           # This does sending and receiving
import struct
import socket
import sys


def recv(connection):
  """reads size of incoming packet and then reads packet"""


  try:
    psize = connection.recv(4)
    psize = struct.unpack('!i', psize)
    message = connection.recv(psize[0])
    message = struct.unpack('!%ds' % psize[0], message)
    message = message[0].decode('utf-8')
    return message
  except TimeoutError:
    print("Timeout")


def send(connection, message):
  """Sends size of packet and then actual packet"""


  message = bytes(message, 'utf-8')
  strsize = len(message)
  message = struct.pack('!%ds' % strsize, message)
  psize = len(message)
  psize = struct.pack('!i', psize)
  connection.send(psize)
  connection.send(message)
