#!/usr/bin/python           # This does sending and receiving
"""Helps with receiving and sending to client and server"""
import struct
import socket


def send(connection, message):
    """Sends size of packet and then actual packet"""
    message = bytes(message, 'utf-8')
    strsize = len(message)
    message = struct.pack('!%ds' % strsize, message)
    psize = len(message)
    psize = struct.pack('!i', psize)
    try:
        connection.send(psize)
        connection.send(message)
        return 1
    except socket.error:
        return -1


def looprecv(sockpeer, msgsize, data):
    """accepts packets 2 bytes at a time"""
    more = sockpeer.recv(2)
    if not more:
        print("Closing client")
        sockpeer.close()
        return -1, data
    else:
        data.extend(more)
        if len(data) == 4 and msgsize == 0:
            msgsize = struct.unpack('!i', data)[0]
            data = bytearray()
        return msgsize, data
