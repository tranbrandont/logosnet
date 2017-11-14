#!/usr/bin/python           # This is server.py file
"""This runs a client for the chatting application"""
import socket
import argparse
import struct

SOCK_LIST  = []

def chat_client(port, ipnum):
    sock=socket.socket()
    if ipnum is None:
        ipnum = socket.gethostname()
    sock.connect((ipnum, port))
    while 1:
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
