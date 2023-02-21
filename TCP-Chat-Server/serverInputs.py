import socket
import threading
import site

# handling server operator inputs
class Operator(threading.Thread):
	def __init__(self, clients):
		threading.Thread.__init__(self)
		self.clients = clients

	# thread initialization
	def run(self):
		# main loop
		while True:
			string = input()
			# passing inputs to handle function
			self.handleData(string)

	def handleData(self, data):
		# checking and handling commands
		if (data[0]=='/'):
			self.command(data)
		# broadcasting
		else: self.announce("Operator: " + data + "\n")

	def announce(self,data):
		for c in self.clients:
			c.socket.sendall(data.encode())


	def command(self,data):
		# parsing command inputs
		strings = data.split()
		# checking for kick command
		if (strings[0]=="/kick"):
			# ensuring name provided
			if (len(strings) < 2):
				print("Missing name.")
			else:
				# looping over clients
				num = 0
				for c in self.clients:
					# telling them to leave
					if c.name == strings[1]:
						c.command("/quit")
						num += 1
				# debug output
				print("Kicked " + str(num) + " people.")
		elif (strings[0]=="/msg"):
			# ensuring all inputs present
			if (len(strings) < 2):
				print("Missing name.")
			elif (len(strings) < 3):
				print("Missing message.")
			else:
				# formatting return string
				s = "Operator (private): "
				for string in strings[2::]:
					s += string + " "
				s = s + "\n"
				# sending to people with that name
				count = 0
				for c in self.clients:
					if c.name == strings[1]:
						count += 1
						c.socket.sendall(s.encode())
				# debug message
				s = "Message sent to " + str(count) + " users of name " + strings[1]
				print(s)
		else:
			# catching unknown commands
			self.socket.sendall("Unrecognized Command\n".encode())
