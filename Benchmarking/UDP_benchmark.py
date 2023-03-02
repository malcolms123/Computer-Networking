import socket
import time

def RunUDPBenchmark(addr,port):
    udpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    data = ['aasdfas','ab','a']


    start = time.time()
    for d in data:
        udpSocket.sendto(d.encode(),(addr,port))
    end = time.time()

    return end-start