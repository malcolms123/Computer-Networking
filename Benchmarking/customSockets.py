import socket

# UDP socket class
class UDPSocket():
    def __init__(self,addr,port,timeout=5):
        self.addr = addr
        self.port = port
        self.skt = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.skt.settimeout(timeout)

    def send(self,packet):
        self.skt.sendto(packet,(self.addr,self.port))

    def receive(self):
        try:
            data, addr = self.skt.recvfrom(4096)
            return data, False
        except:
            return None, True

# TCP socket class
class TCPSocket():
    def __init__(self,addr,port,timeout=5):
        self.addr = addr
        self.port = port
        self.skt = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.skt.connect((self.addr,self.port))
        self.skt.settimeout(1)

    def send(self,packet):
        self.skt.sendall(packet)

    def receive(self):
        try:
            data = self.skt.recv(4096)
            return data, False
        except:
            return None, True