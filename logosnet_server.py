#!/usr/bin/python           # This is server.py file
"""This runs a server for the chatting application"""
import socket
import argparse
import select
import struct
import os
from helper import recv
from helper import send

SOCK_LIST = []


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
				con.setblocking(0)
				SOCK_LIST.append(con)
				psize, username = recv(con)
				if username:
					_messagesize, username = struct.unpack('!I%ds' % ((psize - 4),),
																								 username)
					username = username.decode('utf-8')
					print("client connected (%s)" % username)
					broadcast(serv_sock, con, "[%s] entered our chat room\n" % username)
				else:
					print("client connected (%s, %s)" % _addr)
					broadcast(serv_sock, con, "[%s:%s] entered our chat room\n" % _addr)
			else:
				try:
					psize, message = recv(sock)
					if message:
						_messagesize, message = struct.unpack('!I%ds' % ((psize - 4),),
																									message)
						message = message.decode('utf-8')
						print(message)
						broadcast(serv_sock, sock,
											"\r" + '[' + str(sock.getpeername()) + '] ' + message)
					else:
						if sock in SOCK_LIST:
							SOCK_LIST.remove(sock)
							broadcast(serv_sock, sock, "Client (%s, %s) is offline\n" % _addr)
						sock.close()
				except:
					SOCK_LIST.remove(sock)
					broadcast(serv_sock, sock,
										"Client (%s, %s) is offline, try failed\n" % _addr)
					sock.close()
	serv_sock.close()


def broadcast(serv_sock, sock, message):
	message = bytes(message, 'utf-8')
	strsize = len(message)
	message = struct.pack('!I%ds' % (strsize,), strsize, message)
	for sockpeer in SOCK_LIST:
		if sockpeer != serv_sock and sockpeer != sock:
			try:
				send(sockpeer, message)
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
