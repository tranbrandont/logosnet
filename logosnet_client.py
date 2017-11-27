#!/usr/bin/python           # This is server.py file
"""This runs a client for the chatting application"""
import socket
import argparse
import sys
import select
import struct
import signal
from helper import send
from helper import looprecv

TIMEOUT = 60
MAX_USERNM = 10
MAX_MSG = 1000


def interrupted(_signum, _frame):
    """Signal handler for alarm"""
    print("Did not enter username")
    sys.exit()


class Client:
    """Creates clients for chat service"""
    def send_msg(self, sock, message):
        """Handles sending the message and checking for exit and msg len"""
        if message.strip() == "exit()":
            self.sock.close()
            sys.exit()
        if len(message) < MAX_MSG:
            send(sock, message)
        else:
            print("Message too big")

    def __init__(self, portnum, ip):
        """Runs chat client"""
        self.confirmed = False
        msgsize = 0
        data = bytearray()
        if ip is None:
            ip = socket.gethostname()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, portnum))
        socket_list = [sys.stdin, self.sock]
        signal.signal(signal.SIGALRM, interrupted)
        signal.alarm(TIMEOUT)
        sys.stdout.write("Enter username, max 10 chars: \n\r", )
        sys.stdout.flush()
        while 1:
            read, _write, _error = select.select(socket_list, [], [])
            for sockpeer in read:
                if sockpeer == self.sock:
                    msgsize, data = looprecv(sockpeer, msgsize, data)
                    if msgsize == -1:
                        socket_list.remove(sockpeer)
                        print("Lost connection to server")
                        sys.exit()
                    if len(data) == msgsize:
                        message = struct.unpack('!%ds' % msgsize, data)
                        message = message[0].decode('utf-8')
                        if message == "Unique":
                            print("Username confirmed")
                            self.confirmed = True
                        elif message == "Max # users in server reached\n":
                            print(message)
                            sys.exit()
                        elif message == "Notunique":
                            sys.stdout.write("Username is already in use\n")
                            sys.stdout.write("Enter username, max 10 chars: \n\r", )
                            sys.stdout.flush()
                            signal.alarm(TIMEOUT)
                        else:
                            sys.stdout.write("\r" + message)
                            sys.stdout.flush()
                            #sys.stdout.write("> " + username + ": ")
                            #sys.stdout.flush()
                        msgsize = 0
                        data = bytearray()
                else:
                    if self.confirmed is True:
                        sys.stdout.write("> " + username + ": ")
                        sys.stdout.flush()
                        message = sockpeer.readline()
                        self.send_msg(self.sock, message)
                    else:
                        username = sockpeer.readline().rstrip('\n')
                        signal.alarm(0)
                        if ' ' in username:
                            print("No spaces allowed in username\n")
                            signal.signal(signal.SIGALRM, interrupted)
                            signal.alarm(TIMEOUT)
                            sys.stdout.write("Enter username, max 10 chars: \n\r",)
                            sys.stdout.flush()
                        elif len(username) > 10:
                            sys.stdout.write("Username can't be more than 10 chars")
                            signal.signal(signal.SIGALRM, interrupted)
                            signal.alarm(TIMEOUT)
                            sys.stdout.write("Enter username, max 10 chars: \n\r",)
                            sys.stdout.flush()
                        else:
                            send(self.sock, username)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(add_help=True)
    PARSER.add_argument('--port', type=int, required=True, help='port number')
    PARSER.add_argument('--ip', help='IP address for client')
    ARGS = PARSER.parse_args()
    PORT = ARGS.port
    IPNUM = ARGS.ip
    CLIENTCHAT = Client(PORT, IPNUM)
