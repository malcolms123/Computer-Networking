
import socket
from sys import argv

def RunUDPServer(port):
    udpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    address = udpSocket.bind(('0.0.0.0',port))

    print('UDP echo server up on port ' + str(port))

    while True:
        data,caddress = udpSocket.recvfrom(4096)
        udpSocket.sendto(data,caddress)