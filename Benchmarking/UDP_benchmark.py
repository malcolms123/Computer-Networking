import socket
import time
import threading
import queue


def UDPBenchmarkSend(addr,port,size,nPackets,delay):
    udpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udpSocket.settimeout(1)

    # Do I need to factor in header to size?
    packet = bytes(size)

    q = queue.Queue()

    receiver = threading.Thread(target=UDPBenchmarkReceive,args=[udpSocket,q])
    receiver.start()

    start = time.time()
    lastTime = start
    count = 0
    for i in range(nPackets):
        udpSocket.sendto(packet,(addr,port))
        while time.time() < lastTime + delay:
            pass
        lastTime = time.time()
        count += 1
    endSend = time.time()


    receiver.join()

    endReceive = q.get()
    received = q.get()


    total_time_send = round(1e3*(endSend-start),3)
    total_time_receive = round(1e3*(endReceive-start),3)
    total_sent = count
    loss_rate = round((1-received/count)*100,3)

    return total_time_send, total_time_receive, total_sent, loss_rate

def UDPBenchmarkReceive(udp_socket,q):
    timedOut = False
    count = 0
    while not timedOut:
        try:
            data, addr = udp_socket.recvfrom(4096)
            count += 1
            endTime = time.time()
        except socket.timeout:
            timedOut = True
    q.put(endTime)
    q.put(count)