import argparse
import UDP_benchmark

def parse_args():
    
    parser = argparse.ArgumentParser(description='Echo Server')

    parser.add_argument('--protocol',
                        default='udp',
                        help='Protocol to use [udp,tcp]',
                        choices=['udp','tcp'])
    parser.add_argument('--dst',
                        default = '0.0.0.0',
                        help='Destination IP address.')
    parser.add_argument('--port',
                        help='Destination port.',
                        default=12345,
                        type=int)
    parser.add_argument('--size',
                        help='Packet size in bytes.',
                        default=1000,
                        type=int)
    parser.add_argument('--bandwidth',
                        help='Bandwidth in packets/second.',
                        default=10,
                        type=float)
    parser.add_argument('--distribution',
                        help='Packet distribution over time.',
                        default='burst',
                        choices=['burst','uniform'])
    parser.add_argument('--duration',
                        help='Benchmark duration in seconds.',
                        default=10,
                        type=float)

    return parser.parse_args()

args = parse_args()

print(f"Benchmarking {args.protocol} protocol pinging {args.dst}|{args.port}")

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


if args.protocol == 'udp':
	total_time_send, total_time_receive, total_sent, loss_rate = UDP_benchmark.UDPBenchmarkSend(args.dst,args.port,args.size,nPackets,delay)
elif args.distribution == 'tcp':
    pass
else:
	print('Unknown protocol.')
	quit()

print(f"{total_sent} packets sent over {total_time_send} ms.")
print(f"Final packet received after {total_time_receive} ms.")
print(f"Loss rate: {loss_rate}%")