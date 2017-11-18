#!/usr/bin/python           # This is server.py file
"""This runs a client for the chatting application"""
import socket
import argparse
import sys
import select
import signal
from helper import recv
from helper import send

TIMEOUT = 60
MAX_USERNM = 10
MAX_MSG = 1000


def interrupted(_signum, _frame):
    """Signal handler for alarm"""
    print("Didn't enter username within 60 seconds")
    signal.signal(signal.SIGALRM, interrupted)


def get_user():
    """Gets username, doesn't allow names over 10 chars or with white space"""
    username = ' '
    while ' ' in username or len(username) > MAX_USERNM:
        signal.alarm(TIMEOUT)
        print("Enter a username, max 10 chars: \r", )
        i, _o, _e = select.select([sys.stdin], [], [])
        if i:
            username = sys.stdin.readline().strip()
        signal.alarm(0)
        if ' ' in username:
            print("No spaces allowed in username")
        elif len(username) > 10:
            print("Username can't be more than 10 chars")
    return username


def chat_client(port, ipnum):
    """Runs chat client"""
    if ipnum is None:
        ipnum = socket.gethostname()
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((ipnum, port))
    print(recv(self.sock))
    username = get_user()
    try:
        nonunique = True
        while nonunique:
            send(self.sock, username)
            response = recv(self.sock)
            if response == "Unique":
                nonunique = False
            elif response == "Max # users in server reached":
                print(response)
                self.sock.close()
            else:
                self.sock.close()
                print("Username is taken")
                username = get_user()
    except Exception as err:
        print("Unable to connect" + str(err))
        sys.exit()
    socket_list = [sys.stdin, self.sock]
    while 1:
        read, _write, _error = select.select(socket_list, [], [])
        for sockpeer in read:
            print(username + ": ", )
            if sockpeer == self.sock:
                message = recv(sockpeer)
                if not message:
                    print("Disconnected from server")
                    sys.exit()
                else:
                    sys.stdout.write(message)
            else:
                message = sockpeer.readline()
                print(message)
                send_msg(self.sock, message)


def send_msg(self.sock, message):
    """Handles sending the message and checking for exit and msg len"""
    if message.strip() == "exit()":
        self.sock.close()
        sys.exit()
    if len(message) < MAX_MSG:
        self.send(sock, message)
    else:
        print("Message too big")


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
