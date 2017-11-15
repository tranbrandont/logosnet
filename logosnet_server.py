#!/usr/bin/python           # This is server.py file
"""This runs a server for the chatting application"""
import socket
import argparse
import select
import struct
import os

SOCK_LIST  = []

def chat_server(port, ipnum):
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("Server started")
    if ipnum is None:
        ipnum = socket.gethostname()
    serv_sock.bind((ipnum, port))
    serv_sock.listen(100)
    SOCK_LIST.append(serv_sock)

    while 1:
        read, write, error = select.select(SOCK_LIST, [], [], 0)
        for sock in read:
            if sock == serv_sock:
                con, _addr = serv_sock.accept()
                SOCK_LIST.append(con)
                print("client connected (%s, %s)" % _addr)
                broadcast(serv_sock, con, "[%s:%s] entered our chatting room\n" %_addr)
            else:
                try:
                    data = sock.recv(1000)
                    if data:
                        data = data.decode("utf-8")
                        print(data)
                        broadcast(serv_sock, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)
                    else:
                        if sock in SOCK_LIST:
                            SOCK_LIST.remove(sock)
                            broadcast(serv_sock, sock, "Client (%s, %s) is offline\n" % _addr)
                except:
                    broadcast(serv_sock, sock, "Client (%s, %s) is offline\n" % _addr)
                    continue

    serv_sock.close()





def broadcast(serv_sock, sock, message):
    for sockpeer in SOCK_LIST:
        if sockpeer != serv_sock and sockpeer != sock:
            try:
                sockpeer.send(message)
            except:
                sockpeer.close()
                if sockpeer in SOCK_LIST:
                    SOCK_LIST.remove(sockpeer)




def main():
    """Parses command line arguments, starts client"""
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('--port', type=int, required=True, help='port number')
    parser.add_argument('--ip', help='IP address for client')
    args = parser.parse_args()
    port = args.port
    ipnum = args.ip
    chat_server(port, ipnum)


main()