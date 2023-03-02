import socket

def RunUDPServer(addr,port):
    udpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    address = udpSocket.bind((addr,port))

    print('UDP echo server up on port ' + str(port))

    while True:
        data,caddress = udpSocket.recvfrom(4096)
        print(caddress[0] + '|' + str(caddress[1]) + ': ' + data.decode())
        udpSocket.sendto(data,caddress)