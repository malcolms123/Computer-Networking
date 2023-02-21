import socket
import threading
import sys
from chatClient import Client
from serverInputs import Operator
		

# main server function
def server():
	# initializing a TCP socket
	ssocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	# setting default port
	port = 1234
	# allowing custom port
	if (len(sys.argv) > 1):
		port = int(sys.argv[1])
	else: print("Defaulting to port " + str(port))
	# setting and binding to address
	saddress = (('0.0.0.0',port))
	ssocket.bind(saddress)
	# begin listening and print opening message
	ssocket.listen()
	print('Server Started on port ' + str(port))
	# prepare to save clients
	clients = []
	# creating thread to listen for server operator inputs
	Operator(clients).start()
	# main loop
	while True:
		# accepting a connection
		csocket,caddress = ssocket.accept()
		# passing client to a thread
		newClient = Client(csocket,caddress,clients)
		newClient.start()
		# keeping track of connections
		clients.append(newClient)
		# announcing new user
		for c in clients:
			s = 'Welcome ' + newClient.name + ' to the server!\n'
			c.socket.send(s.encode())
		print(s[0:-1])

server()