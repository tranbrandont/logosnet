#!/usr/bin/python           # This does sending and receiving
"""Helps with receiving and sending to client and server"""
import struct


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


def looprecv(sockpeer, msgsize, data):
    """accepts packets 2 bytes at a time"""
    if msgsize == 0:
        if len(data) < 4:
            more = sockpeer.recv(2)
            data.extend(more)
        if not more:
            print("Closing client")
            sockpeer.close()
            return -1, data
        if len(data) >= 4:
            print(data)
            msgsize = struct.unpack('!i', data)[0]
            data = bytearray()
        return msgsize, data
    elif msgsize - len(data) == 1:
        more = sockpeer.recv(1)
        data.extend(more)
        return msgsize, data
    elif len(data) < msgsize:
        more = sockpeer.recv(2)
        data.extend(more)
        return msgsize, data

