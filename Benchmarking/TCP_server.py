import socket

def RunTCPServer(addr,port):
	tcpSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	tcpSocket.bind((addr,port))
	tcpSocket.listen()

	print('TCP echo server up on port ' + str(port))

	while True:
		csocket, caddress = tcpSocket.accept()
		callCard = caddress[0] + '|' + str(caddress[1])
		print(callCard + ' connected.')
		connected = True

		pcount = 0

		while connected:
			data = csocket.recv(4096)
			if len(data) == 0:
				print(callCard + ' disconnected.')
				connected = False
			else:
				# print(callCard + ': ' + data.decode())
				pcount += 1
				# print(f"Packets echoed: {pcount}")
				csocket.sendall(data)

