import argparse, customSockets, queue, threading, time

# function for parsing arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Traffic Generator')
    parser.add_argument('--protocol',default='udp',help='Protocol to use [udp,tcp]',choices=['udp','tcp'])
    parser.add_argument('--dst',default = '0.0.0.0',help='Destination IP address.')
    parser.add_argument('--port',help='Destination port.',default=12345,type=int)
    parser.add_argument('--size',help='Packet size in bytes.',default=1000,type=int)
    parser.add_argument('--bandwidth',help='Bandwidth in packets/second.',default=10,type=float)
    parser.add_argument('--distribution',help='Packet distribution over time.',default='burst',choices=['burst','uniform'])
    parser.add_argument('--duration',help='Benchmark duration in seconds.',default=10,type=float)
    return parser.parse_args()

# function for receiving a stream of packets until timeout
def BenchmarkReceive(benchmarker,q):
    # storing timeout boolean and received packet count
    timedOut = False
    count = 0
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
    # pass information to main thread
    q.put(endTime)
    q.put(count)

# parsing command line arguments
args = parse_args()

# announce benchmark
print(f"Benchmarking {args.protocol} protocol pinging {args.dst}|{args.port}")

# calculate packet count and delays based on arguments
nPackets = int(args.bandwidth*args.duration)
if args.distribution == 'burst':
    delay = 0
    print(f"Bursting {nPackets} packets of size {args.size} bytes.")
elif args.distribution == 'uniform':
    delay = 1/args.bandwidth
    print(f"Sending {nPackets} packets of size {args.size} bytes uniformly over {args.duration} seconds.")
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



# Do I need to factor in header to size?
packet = bytes(args.size)

q = queue.Queue()

receiver = threading.Thread(target=BenchmarkReceive,args=[benchmarker,q])
receiver.start()

start = time.time()
lastTime = start
count = 0
for i in range(nPackets):
    benchmarker.send(packet)
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

print(f"{total_sent} packets sent over {total_time_send} ms.")
print(f"Final packet received after {total_time_receive} ms.")
print(f"Loss rate: {loss_rate}%")