#!/usr/bin/python           # This is server.py file


"""IF USERNAME ISN'T IN LIST ASK FOR USERNAME"""
"""This runs a server for the chatting application"""
import socket
import argparse
import select
import sys
import struct
from helper import recv
from helper import send
from helper import looprecv

SOCK_LIST = []
WRITE_LIST = []
USER_SOCK_DICT = {}


def accept_client(serv_sock):
    """Accepts clients into the server or rejects if names aren't unique or
    max number of users in server"""
    con, _addr = serv_sock.accept()
    con.setblocking(0)
    SOCK_LIST.append(con)

    if len(SOCK_LIST) >= 100:
        send(con, "Max # users in server reached")
        con.close()


def take_username(con, serv_sock, write, username):
    print(username)
    if not username:
        if con in SOCK_LIST:
            SOCK_LIST.remove(con)
        con.close()
    elif any(username == user for user in
           USER_SOCK_DICT.values()):
        send(con, "Notunique")
        print("client connected Anonymous")
        broadcast(serv_sock, con, write, "Anonymous entered our chat room\n")
        USER_SOCK_DICT[con] = ' '
    else:
        USER_SOCK_DICT[con] = username
        send(con, "Unique")
        print("User {} connected".format(username))
        broadcast(serv_sock, con, write,
                  "{} entered our chat room\n".format(username))
        WRITE_LIST.append(con)


def message_handle(message, sock, serv_sock, write):
    """Handles incoming messages and redirects them to clients"""
    if message:
        if message[:1] == '@':
            notfound = 1
            privatemessage = message.split(' ', 1)
            print(privatemessage[0])
            friend = privatemessage[0][1:len(privatemessage[0])]
            for user, name in USER_SOCK_DICT.items():
                if friend == name:
                    send(user, "> " + USER_SOCK_DICT.get(sock) + ": " + message)
                    notfound = 0
            if notfound:
                send(sock, "User " + friend + " not connected")
        else:
            broadcast(serv_sock, sock, write,
                      "> " + USER_SOCK_DICT.get(sock) + ': ' + message)
    else:
        if sock in SOCK_LIST:
            SOCK_LIST.remove(sock)
            if sock in WRITE_LIST:
                WRITE_LIST.remove(sock)
            broadcast(serv_sock, sock, write, "Client {} is offline\n".format(
                USER_SOCK_DICT.get(sock) if USER_SOCK_DICT.get(
                    sock) is not None else"Anonymous"))
            del USER_SOCK_DICT[sock]
        sock.close()


def chat_server(port, ipnum):
    """Starts chat server"""
    msgsize = 0
    data = bytearray()
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.setblocking(0)
    print("Server started")
    if ipnum is None:
        ipnum = socket.gethostname()
    serv_sock.bind((ipnum, port))
    serv_sock.listen(1000)
    SOCK_LIST.append(serv_sock)

    while 1:
        read, write, _error = select.select(SOCK_LIST, [], [])
        for sock in read:
            if sock == serv_sock:
                accept_client(serv_sock)
            else:
                msgsize, data = looprecv(sock, msgsize, data)
                if len(data) == msgsize:
                    message = struct.unpack('!%ds' % msgsize, data)
                    message = message[0].decode('utf-8')
                    msgsize = 0
                    data = bytearray()
                    if USER_SOCK_DICT.get(sock) == ' ' or USER_SOCK_DICT.get(sock) is None:
                        write = WRITE_LIST
                        take_username(sock, serv_sock, write, message)
                    else:
                        write = WRITE_LIST
                        message_handle(message, sock, serv_sock, write)


def broadcast(serv_sock, sock, write, message):
    """sends messages to all clients except sending client"""
    for sockpeer in write:
        if sockpeer != serv_sock and sockpeer != sock:
            try:
                send(sockpeer, message)
            except:
                sockpeer.close()
                if sockpeer in SOCK_LIST:
                    SOCK_LIST.remove(sockpeer)
                    WRITE_LIST.remove(sockpeer)
                    USER_SOCK_DICT.pop(sockpeer)


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
