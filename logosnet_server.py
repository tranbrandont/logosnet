#!/usr/bin/python           # This is server.py file
"""This runs a server for the chatting application"""
import socket
import argparse
import select
from helper import recv
from helper import send

SOCK_LIST = []
WRITE_LIST = []
USER_SOCK_DICT = {}


def accept_client(serv_sock, write):
    """Accepts clients into the server or rejects if names aren't unique or
    max number of users in server"""
    con, _addr = serv_sock.accept()
    send(con, "You are connected")
    if len(SOCK_LIST) >= 100:
        send(con, "Max # users in server reached")
        con.close()
    else:
        SOCK_LIST.append(con)
        username = recv(con)
        if any(username in user for user in
               USER_SOCK_DICT.values()):
            send(con, "Notunique")
            print("client connected Anonymous")
            broadcast(serv_sock, con, write, "Anonymous entered our chat room\n")
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
            privatemessage = message.split(' ', 1)[0]
            friend = privatemessage[1:len(privatemessage)]
            print(friend)
            for user, name in USER_SOCK_DICT.items():
                if friend == name:
                    send(user, "> " + message)
        else:
            broadcast(serv_sock, sock, write,
                      "> " + USER_SOCK_DICT.get(sock) + ': ' + message)
    else:
        if sock in SOCK_LIST:
            SOCK_LIST.remove(sock)
            WRITE_LIST.remove(sock)
            broadcast(serv_sock, sock, write, "Client {} is offline\n".format(
                USER_SOCK_DICT.get(sock) if USER_SOCK_DICT.get(
                    sock) is not None else"Anonymous"))
            USER_SOCK_DICT.pop(sock)
        sock.close()


def chat_server(port, ipnum):
    """Starts chat server"""
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.setblocking(0)
    print("Server started")
    if ipnum is None:
        ipnum = socket.gethostname()
    serv_sock.bind((ipnum, port))
    serv_sock.listen(100)
    SOCK_LIST.append(serv_sock)

    while 1:
        read, write, _error = select.select(SOCK_LIST, WRITE_LIST, [])
        for sock in read:
            if sock == serv_sock:
                accept_client(serv_sock, write)
            else:
                try:
                    message = recv(sock)
                    message_handle(message, sock, serv_sock, write)
                except:
                    SOCK_LIST.remove(sock)
                    WRITE_LIST.remove(sock)
                    broadcast(serv_sock, sock, write,
                              "Client {} is offline\n".format(
                                  USER_SOCK_DICT.get(
                                      sock) if USER_SOCK_DICT.get(
                                          sock) is not None else "Anonymous"))
                    USER_SOCK_DICT.pop(sock)
                    sock.close()


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
                    WRITE_LIST.remove(sock)
                    USER_SOCK_DICT.pop(sock)


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
