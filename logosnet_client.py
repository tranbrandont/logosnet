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


class Client:
    """Creates clients for chat service"""
    def interrupted(self, _signum, _frame):
        """Signal handler for alarm"""
        print("Didn't enter username within 60 seconds")
        sys.exit()


    @staticmethod
    def get_user():
        """Gets username, doesn't allow names over 10 chars
        or with white space"""
        username = ' '
        while ' ' in username or len(username) > MAX_USERNM:
            signal.signal(signal.SIGALRM, self.interrupted)
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
        username = self.get_user()
        if ip is None:
            ip = socket.gethostname()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, portnum))
        print(recv(self.sock))
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
                    username = self.get_user()
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
                    self.send_msg(self.sock, message)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(add_help=True)
    PARSER.add_argument('--port', type=int, required=True, help='port number')
    PARSER.add_argument('--ip', help='IP address for client')
    ARGS = PARSER.parse_args()
    PORT = ARGS.port
    IPNUM = ARGS.ip
    CLIENTCHAT = Client(PORT, IPNUM)
