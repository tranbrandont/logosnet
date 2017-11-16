#!/usr/bin/python           # This is server.py file
"""This runs a client for the chatting application"""
import socket
import argparse
import struct
import sys
import select
from helper import recv
from helper import send



def chat_client(port, ipnum):
    username = input("Enter a username, max 10 chars: ")
    sock = socket.socket()

    if ipnum is None:
        ipnum = socket.gethostname()
    try:
        sock.connect((ipnum, port))
        username = bytes(username, 'utf-8')
        strsize = len(username)
        username = struct.pack('!I%ds' % (strsize,), strsize, username)
        send(sock, username)
    except:
        print("Unable to connect")
        sys.exit()
    socket_list = [sys.stdin, sock]
    outgoing = [sock]
    while 1:
        read, write, error = select.select(socket_list, outgoing, [])

        for sockpeer in read:
            if sockpeer == sock:
                psize, message = recv(sockpeer)
                if not message:
                    print("Disconnected from server")
                    sys.exit()
                else:
                    _messagesize, message = struct.unpack('!I%ds' % ((psize - 4),), message)
                    message = message.decode('utf-8')
                    sys.stdout.write(message)
            else:
                message = sockpeer.readline()
                message = bytes(message, 'utf-8')
                strsize = len(message)
                message = struct.pack('!I%ds' % (strsize,), strsize, message)
                send(sock, message)




def main():
    """Parses command line arguments, starts client"""
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('--port', type=int, required=True, help='port number')
    parser.add_argument('--ip', help='IP address for client')
    args = parser.parse_args()
    port = args.port
    ipnum = args.ip
    chat_client(port, ipnum)



main()
