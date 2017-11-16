#!/usr/bin/python           # This does sending and receiving
import struct
import socket


def recv(connection):
    """reads size of incoming packet and then reads packet"""
    try:
        psize = connection.recv(4)
        psize = struct.unpack('!i', psize)

        return psize[0], connection.recv(psize[0])
    except TimeoutError:
        print("Timeout")


def send(connection, message):
    """Sends size of packet and then actual packet"""
    psize = len(message)
    psize = struct.pack('!i', psize)
    connection.send(psize)
    connection.send(message)

