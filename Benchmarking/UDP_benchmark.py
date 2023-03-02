import socket
import time
import threading

end = 0

def UDPBenchmarkSend(addr,port,size):
    udpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udpSocket.settimeout(5)

    packet = bytes(size)

    receiver = threading.Thread(target=UDPBenchmarkReceive,args=(udpSocket))
    receiver.start()

    start = time.time()
    for i in range(1000):
        udpSocket.sendto(packet,(addr,port))
        udpSocket.recvfrom(4096)

    receiver.join()

    return end-start

def UDPBenchmarkReceive(socket):
    timedOut = False
    while not timedOut:
        try:
            data, addr = udp_socket.recvfrom(4096)
            endTime = time.time()
        except socket.timeout:
            timedOut = True
    end = endTime