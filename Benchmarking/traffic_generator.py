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
                        default=1000,
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

if args.protocol == 'udp':
	result = UDP_benchmark.RunUDPBenchmark(args.dst,args.port)
elif args.distribution == 'tcp':
    pass
else:
	print('Unknown protocol.')
	quit()

print(result)