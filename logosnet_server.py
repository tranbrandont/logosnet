#!/usr/bin/python           # This is server.py file
"""This runs a server for the chatting application"""
import socket
import argparse
import select
import struct
import os
import time
from helper import recv
from helper import send

SOCK_LIST = []
USER_SOCK_DICT = {}



def chat_server(port, ipnum):
	serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serv_sock.setblocking(0)
	print("Server started")
	if ipnum is None:
		ipnum = socket.gethostname()
	serv_sock.bind((ipnum, port))
	serv_sock.listen(100)
	SOCK_LIST.append(serv_sock)

	while 1:
		read, write, error = select.select(SOCK_LIST, [], [])
		for sock in read:
			if sock == serv_sock:
				con, _addr = serv_sock.accept()
				if len(SOCK_LIST) >= 100:
					send(con, "Max # users in server reached")
					close(con)
				else:
					SOCK_LIST.append(con)
					username = recv(con)
					if any(username in user for user in USER_SOCK_DICT.values()):
						send(con, "Notunique")
						print("client connected Anonymous")
						broadcast(serv_sock, con, "Anonymous entered our chat room\n")
					else:
						USER_SOCK_DICT[con] = username
						send(con, "Unique")
						print("User {} connected".format(username))
						broadcast(serv_sock, con, "{} entered our chat room\n".format(username))
			else:
				try:
					message = recv(sock)
					if message:
						if message[:1] == '@':
							privatemessage = message.split(' ', 1)[0]
							friend = privatemessage[1:len(privatemessage)]
							print(friend)
							for user, name in USER_SOCK_DICT.items():
								if friend == name:
									send(user, "> " + message)
						else:
							broadcast(serv_sock, sock, "> " + USER_SOCK_DICT.get(sock) + ': ' + message)
					else:
						if sock in SOCK_LIST:
							SOCK_LIST.remove(sock)
							broadcast(serv_sock, sock, "Client {} is offline\n".format(USER_SOCK_DICT.get(sock) if USER_SOCK_DICT.get(sock) is not None else "Anonymous"))
							USER_SOCK_DICT.pop(sock)
						sock.close()
				except:
					SOCK_LIST.remove(sock)
					broadcast(serv_sock, sock,
										"Client {} is offline\n".format(USER_SOCK_DICT.get(sock) if USER_SOCK_DICT.get(sock) is not None else "Anonymous"))
					USER_SOCK_DICT.pop(sock)
					sock.close()

def broadcast(serv_sock, sock, message):
	for sockpeer in SOCK_LIST:
		if sockpeer != serv_sock and sockpeer != sock:
			try:
				send(sockpeer, message)
			except:
				sockpeer.close()
				if sockpeer in SOCK_LIST:
					SOCK_LIST.remove(sockpeer)
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
