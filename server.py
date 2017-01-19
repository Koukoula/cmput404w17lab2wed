#!/user/bin/env python

import socket, os, sys, errno

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serverSocket.bind(("0.0.0.0", 8000))
serverSocket.listen(5)

while True:
	(incomingSocket, address) = serverSocket.accept()
	print "Got a connection from %s" % (repr(address))
	#Reap to kill all the zombies we are making.
	try:
		reaped = os.waitpid(0, os.WNOHANG)
	except OSError, e:
		if e.errno == errno.ECHILD:
			pass
		else:
			raise
	else:	
		print "Reaped %s" % (repr(reaped))

	
	if (os.fork() != 0):
		#if parent, loop back around
		continue

	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# AF_INET means we want an IPv4 socket
	# SOCK_STREAM means we want a TCP socket


	clientSocket.connect(("www.google.com", 80))
	incomingSocket.setblocking(0)
	clientSocket.setblocking(0)
	while True: 
		#connection isn't instant, so we need to keep looting.
		#No longer get stuck on lines like part = incomingSocket.recv(1024)
		# and part = clientSocket.recv(1024)
		#This causes an error where it would get stuck, so we placed it arround a try except block
		request = bytearray()
		while True:
			#Loop: Try to read, if nothing to read, break
			try:
				part = incomingSocket.recv(1024)
			except IOError, e:
				if e.errno == socket.errno.EAGAIN:
				#Make sure to catch this specific error, and not all related errors.
					break
				else:
					raise
			if (part):
				request.extend(part)
				clientSocket.sendall(part)
			else: 
				sys.exit(0) # Quits program, because breaking leaves children running and eats up mem.
		if len(request) > 0:
			print(request)

		response = bytearray()
		while True:
			try:
				part = clientSocket.recv(1024)
			except IOError, e:
				if e.errno == socket.errno.EAGAIN:
				#Make sure to catch this specific error, and not all related errors.
					break
				else:
					raise
			if (part):
				response.extend(part)
				incomingSocket.sendall(part)
			else: 
				sys.exit(0)
		if len(response) > 0:	
			print(response)

		#Dear OS. Wait for one of the following things to happen.
		select.select(
			[incommingSocket, clientSocket], #read
			[],				#write
			[incomingSocket, clientSocket], #exceptions
			1.0)				#timeout
