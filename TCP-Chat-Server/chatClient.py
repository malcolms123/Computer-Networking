import socket
import threading

# handle connections class
class Client(threading.Thread):
	def __init__(self,csocket,caddress,others):
		threading.Thread.__init__(self)
		# saving information about connection
		self.socket = csocket
		self.ip = caddress[0]
		self.port = caddress[1]
		self.name = self.ip + "|" + str(self.port)
		self.others = others
		self.open = True

	def run(self):
		# main loop
		while self.open:
			# listening for data
			data = self.socket.recv(4096)
			# passing data to handle function
			self.handleData(data)

	def handleData(self, data):
		data = data.decode()
		# catching keyboard interrupt
		if (len(data)==0):
			data = "/quit"
		# checking for commands
		if (data[0]=='/'):
			self.command(data)
		# broadcasting
		else: self.announce(self.name + ": " + data)

	def announce(self,data):
		# prettying up output for terminal display
		if (data[-1] == "\n"):
			pdata = data[0:-1]
			print(pdata)
		else: print(data)
		# broadcasting to all other connections
		for other in self.others:
			if (other != self):
				other.socket.sendall(data.encode())

	def command(self,data):
		# parsing command data
		strings = data.split()
		# nickname command
		if (strings[0]=="/nick"):
			# saving, changing, and announcing name change
			old = self.name
			self.name = strings[1]
			self.announce(old + " is now " + self.name + "\n")
			toSelf = "You are now " + self.name + "\n"
			self.socket.sendall(toSelf.encode())
		# list command
		elif (strings[0]=="/list"):
			# looping over other clients
			for other in self.others:
				# checking not own connection
				if (other != self):
					# sending information about other connections
					s = other.ip + "|" + str(other.port) + " as " + other.name + "\n"
					self.socket.sendall(s.encode())
		# quit command
		elif (strings[0]=="/quit"):
			# announcing leaving
			self.announce(self.name + " has left the server.\n")
			self.socket.sendall("You have left the server\n".encode())
			# removing from client list
			self.others.remove(self)
			# closing connection
			self.socket.close()
			# ending main loop
			self.open = False
		# message command
		elif (strings[0]=="/msg"):
			# ensuring all inputs present
			if (len(strings) < 2):
				self.socket.sendall("Missing name.\n".encode())
			elif (len(strings) < 3):
				self.socket.sendall("Missing message.\n".encode())
			else:
				# formatting return string
				s = self.name + "(private): "
				for string in strings[2::]:
					s += string + " "
				s = s + "\n"
				# sending to people with that name
				count = 0
				for other in self.others:
					if other.name == strings[1]:
						count += 1
						other.socket.sendall(s.encode())
				# debug message
				s = "Message sent to " + str(count) + " users of name " + strings[1] + "\n"
				self.socket.sendall(s.encode())
		else:
			# catching unknown commands
			self.socket.sendall("Unrecognized Command\n".encode())


