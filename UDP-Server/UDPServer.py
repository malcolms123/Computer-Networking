import socket
from sys import argv

def RunServer():
    port = 12345
    if (len(argv)>1):
        port = int(argv[1])
    udpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    address = udpSocket.bind(('0.0.0.0',port))


    print('server is up on port ' + str(port))

    clients = []
    while True:
        data,caddress = udpSocket.recvfrom(4096)
        print(caddress[0] + "|" + str(caddress[1]) + ": " + data.decode()[0:-1])
        if (clients.count(caddress) == 0):
            clients.append(caddress)
        data = data.decode()
        data = caddress[0] + ": " + data
        for c in clients:
            if (c != caddress):
                udpSocket.sendto(data.encode(),c)


RunServer()