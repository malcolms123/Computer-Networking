import argparse, customSockets, queue, threading, time, struct, statistics

# function for parsing arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Traffic Generator')
    parser.add_argument('--protocol',default='udp',help='Protocol to use [udp,tcp]',choices=['udp','tcp'])
    parser.add_argument('--dst',default = '0.0.0.0',help='Destination IP address.')
    parser.add_argument('--port',help='Destination port.',default=12345,type=int)
    parser.add_argument('--size',help='Packet size in bytes.',default=100,type=int)
    parser.add_argument('--bandwidth',help='Bandwidth in packets/second.',default=10,type=float)
    parser.add_argument('--distribution',help='Packet distribution over time.',default='burst',choices=['burst','uniform'])
    parser.add_argument('--duration',help='Benchmark duration in seconds.',default=10,type=float)
    return parser.parse_args()

# function for receiving a stream of packets until timeout
def BenchmarkReceive(benchmarker,q,size):
    # storing timeout boolean and received packet count
    timedOut = False
    endTime = time.time()
    count = 0
    lastSeqNo = -1
    lastLastSeqNo = -2
    RTTs = []
    OOOs = []
    # listening until timedout
    while not timedOut:
        # receive data
        data, timeout = benchmarker.receive()
        if timeout:
            timedOut = True
        else:
            # count received packet and time
            count += 1
            endTime = time.time()
            seqno = struct.unpack("!Q",data[0:8])[0]
            sendTime = struct.unpack("!Q",data[8:16])[0]/1e9
            RTTs.append(endTime-sendTime)
            if lastLastSeqNo < lastSeqNo and lastSeqNo < seqno:
                OOOs.append(False)
            else:
                OOOs.append(True)
            lastLastSeqNo = lastSeqNo
            lastSeqNo += 1
    # pass information to main thread
    q.put(endTime)
    q.put(count)
    q.put(RTTs)
    q.put(OOOs)

# parsing command line arguments
args = parse_args()

# announce benchmark
print(f"Benchmarking {args.protocol} protocol pinging {args.dst}|{args.port}")

# calculate packet count and delays based on arguments
nPackets = int(args.bandwidth*args.duration)
if args.distribution == 'burst':
    delay = 0
    print(f"Attempting to burst {nPackets} packets of size {args.size} bytes.")
elif args.distribution == 'uniform':
    delay = 1/args.bandwidth
    print(f"Attempting to send {nPackets} packets of size {args.size} bytes uniformly over {args.duration} seconds.")
else:
    print('Unknown distribution.')
    quit()

# define the benchmark client depending on protocol
if args.protocol == 'udp':
    benchmarker = customSockets.UDPSocket(args.dst,args.port)
elif args.protocol == 'tcp':
    benchmarker = customSockets.TCPSocket(args.dst,args.port)
else:
	print('Unknown protocol.')
	quit()

# packet reception done with threading
q = queue.Queue()
receiver = threading.Thread(target=BenchmarkReceive,args=[benchmarker,q,args.size])
receiver.start()

# preparing to send
start = time.time()
cutoff = start + args.duration
lastTime = start
count = 0
# sending until out of time
for i in range(nPackets):
    # cutting of send if time limit reached
    if time.time() >= cutoff:
        break
    # delaying before sending
    while time.time() < lastTime + delay:
        pass
    lastTime = time.time()
    # preparing packet
    seqno = struct.pack("!Q",i)
    send_time_ns = struct.pack("!Q",int(1e9 * time.time()))
    payload = seqno + send_time_ns
    packet = payload + bytes(args.size-16)
    # sending packet
    benchmarker.send(packet)
    count += 1
endSend = time.time()

# waiting for receiver to finish
receiver.join()
# interpretting from reception thread
endReceive = q.get()
received = q.get()
RTTs = q.get()
OOOs = q.get()

# calculating statistics
total_time_send = round(1e3*(endSend-start),3)
total_time_receive = round(1e3*(endReceive-start),3)
total_sent = count
loss_rate = round((1-received/count)*100,3)
ooo_count = OOOs.count(True)
ooo_rate = round((ooo_count/received)*100,3)
min_rtt = round(min(RTTs)*1e3,3)
avg_rtt = round(sum(RTTs)/len(RTTs)*1e3,3)
med_rtt = round(statistics.median(RTTs)*1e3,3)
max_rtt = round(max(RTTs)*1e3,3)

# printing results
print(f"{total_sent} packets sent over {total_time_send} ms.")
print(f"Final packet received after {total_time_receive} ms.")
print(f"Loss rate: {loss_rate}%")
print(f"OOO rate: {ooo_rate}%")
print(f"RTT min/mean/median/max: {min_rtt}/{avg_rtt}/{med_rtt}/{max_rtt} ms.")