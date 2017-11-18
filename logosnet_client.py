#!/usr/bin/python           # This is server.py file
"""This runs a client for the chatting application"""
import socket
import argparse
import struct
import sys
import select
import signal
import string
from helper import recv
from helper import send

TIMEOUT = 60
MAX_USERNM = 10
MAX_MSG = 1000

def interrupted(signum, frame):
	print("Didn't enter username within 60 seconds")
	signal.signal(signal.SIGALRM, interrupted)


def get_user():
	username = ' '
	while ' ' in username or len(username) > MAX_USERNM:
		signal.alarm(TIMEOUT)
		print("Enter a username, max 10 chars: \r",)
		i, o, e = select.select([sys.stdin], [], [])
		if i:
			username = sys.stdin.readline().strip()
		signal.alarm(0)
		if ' ' in username:
			print("No spaces allowed in username")
		elif len(username) > 10:
			print("Username can't be more than 10 chars")
	return username


def chat_client(port, ipnum):
	username = get_user()
	if ipnum is None:
		ipnum = socket.gethostname()
	try:
		nonunique = True
		while nonunique:
			sock = socket.socket()
			sock.connect((ipnum, port))
			send(sock, username)
			response = recv(sock)
			if response == "Unique":
				nonunique = False
			elif response == "Max # users in server reached":
				print(response)
				sock.close()
			else:
				sock.close()
				print("Username is taken")
				username = get_user()
	except Exception as e:
		print("Unable to connect" + str(e))

		sys.exit()
	socket_list = [sys.stdin, sock]
	while 1:
		read, write, error = select.select(socket_list, [], [])

		for sockpeer in read:
			print(username + ": ",)
			if sockpeer == sock:
				message = recv(sockpeer)
				if not message:
					print("Disconnected from server")
					sys.exit()
				else:
					sys.stdout.write(message)
			else:
				message = sockpeer.readline()
				print(message)
				if message.strip() == "exit()":
					sock.close()
					sys.exit()
				if len(message) < MAX_MSG:
					send(sock, message)
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
