#!/usr/bin/python           # This is server.py file


"""This runs a server for the chatting application"""
import socket
import argparse
import select
import struct
from helper import send
from helper import looprecv

SOCK_LIST = []
WRITE_LIST = []
USER_SOCK_DICT = {}
USER_MSG_DICT = {}


def rmv_client(sock):
    """removes clients from lists and dicts and closes sock"""
    if sock in SOCK_LIST:
        SOCK_LIST.remove(sock)
    if sock in WRITE_LIST:
        WRITE_LIST.remove(sock)
    if sock in USER_SOCK_DICT:
        del USER_SOCK_DICT[sock]
    if sock in USER_MSG_DICT:
        del USER_MSG_DICT[sock]
    sock.close()


def accept_client(serv_sock):
    """Accepts clients into the server or rejects if names aren't unique or
    max number of users in server"""
    try:
        con, _addr = serv_sock.accept()
        con.setblocking(0)
        if len(SOCK_LIST) >= 256:
            send(con, "Max # users in server reached")
            con.close()
        else:
            SOCK_LIST.append(con)
            WRITE_LIST.append(con)
            USER_MSG_DICT[con] = [0, bytearray()]
            if send(con, "You are connected\n") == -1:
                broadcast(serv_sock, con, WRITE_LIST, "User {} has left\n".format(
                    USER_SOCK_DICT.get(con) if USER_SOCK_DICT.get(
                        con) is not None else "Anonymous"))
                rmv_client(con)
    except:
        print("Can't accept?")


def take_username(con, serv_sock, write, username):
    """Takes usernames from clients"""
    if not username:
        rmv_client(con)
    elif any(username == user for user in
             USER_SOCK_DICT.values()):
        if send(con, "Notunique") == -1:
            rmv_client(con)
    else:
        USER_SOCK_DICT[con] = username
        if send(con, "Unique") == -1:
            rmv_client(con)
        else:
            broadcast(serv_sock, con, write,
                      "User {} has joined\n".format(username))
            send(con, "User {} has joined\n".format(username))


def message_handle(message, sock, serv_sock, write):
    """Handles incoming messages and redirects them to clients"""
    if message:
        if message[:1] == '@':
            notfound = 1
            privatemessage = message.split(' ', 1)
            friend = privatemessage[0][1:len(privatemessage[0])]
            for user, name in USER_SOCK_DICT.items():
                if friend == name:
                    if send(user, "> " + USER_SOCK_DICT.get(sock) + ": " + message) == -1:
                        if sock in SOCK_LIST:
                            SOCK_LIST.remove(sock)
                            WRITE_LIST.remove(sock)
                            del USER_SOCK_DICT[sock]
                            del USER_MSG_DICT[sock]
                        sock.close()
                    notfound = 0
            if notfound:
                if send(sock, "User " + friend + " not connected\n") == -1:
                    rmv_client(sock)
        else:
            broadcast(serv_sock, sock, write,
                      "> " + USER_SOCK_DICT.get(sock) + ': ' + message)
    else:
        broadcast(serv_sock, sock, write, "User {} has left\n".format(
            USER_SOCK_DICT.get(sock) if USER_SOCK_DICT.get(
                sock) is not None else "Anonymous"))
        rmv_client(sock)


def chat_server(port, ipnum):
    """Starts chat server"""
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv_sock.setblocking(0)
    print("Server started")
    if ipnum is None:
        ipnum = socket.gethostname()
    serv_sock.bind((ipnum, port))
    serv_sock.listen(100)
    SOCK_LIST.append(serv_sock)
    while 1:
        read, write, error = select.select(SOCK_LIST, [], SOCK_LIST)
        for sock in read:
            if sock == serv_sock:
                accept_client(serv_sock)
            else:
                msgsize = USER_MSG_DICT.get(sock)[0]
                data = USER_MSG_DICT.get(sock)[1]
                msgsize, data = looprecv(sock, msgsize, data)
                USER_MSG_DICT[sock] = [msgsize, data]
                if msgsize == -1:
                    write = WRITE_LIST
                    broadcast(serv_sock, sock, write, "User {} has left\n".format(
                        USER_SOCK_DICT.get(sock) if USER_SOCK_DICT.get(
                            sock) is not None else "Anonymous"))

                if len(data) == msgsize:
                    message = struct.unpack('!%ds' % len(data), data)
                    message = message[0].decode('utf-8')
                    msgsize = 0
                    data = bytearray()
                    USER_MSG_DICT[sock] = [msgsize, data]
                    if USER_SOCK_DICT.get(sock) == ' ' or USER_SOCK_DICT.get(sock) is None:
                        write = WRITE_LIST
                        take_username(sock, serv_sock, write, message)
                    else:
                        write = WRITE_LIST
                        message_handle(message, sock, serv_sock, write)
        for sock in error:
            print("Handling exception for {}".format(USER_SOCK_DICT.get(sock)))
            rmv_client(sock)


def broadcast(serv_sock, sock, write, message):
    """sends messages to all clients except sending client"""
    for sockpeer in write:
        print(message + " in loop")
        if sockpeer != serv_sock and sockpeer != sock:
            print(USER_SOCK_DICT.get(sockpeer))
            if send(sockpeer, message) == -1:
                rmv_client(sock)


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
