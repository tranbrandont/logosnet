#!/usr/bin/python           # This is server.py file
"""This runs a client for the chatting application"""
import socket
import argparse
import struct

SOCK_LIST  = []

def chat_client(port, ipnum):
    sock = socket.socket()
    if ipnum is None:
        ipnum = socket.gethostname()
    try:
        sock.connect((ipnum, port))
    except:
        print("Unable to connect")
        sys.exit()
    while 1:
        socket_list = [sys.stdin, sock]

        read, write, error = select.select(socket_list, [], [])

        for sockpeer in read:
            if sockpeer == sock:
                data = sock.recv(4096)
                if not data:
                    print("Disconnected from server")
                    sys.exit()
                else:
                    sys.stdout.write(data)
            else:
                message = input()
                message = bytes(message, 'utf-8')
                sock.send(message)




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
