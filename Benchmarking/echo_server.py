import argparse
import UDP_server
import TCP_server

# parse command line inputs
def parse_args():
    parser = argparse.ArgumentParser(description='Echo Server')
    parser.add_argument('--protocol',default='udp',help='Protocol to use [udp,tcp]',choices=['udp','tcp'])
    parser.add_argument('--addr',default = '0.0.0.0',help='IP address to run server on.')
    parser.add_argument('--port',help='Port to run server on.',default=12345,type=int)
    return parser.parse_args()
args = parse_args()

# running proper server
if args.protocol == 'udp':
    UDP_server.RunUDPServer(args.addr,args.port)
elif args.protocol == 'tcp':
    TCP_server.RunTCPServer(args.addr,args.port)
else:
    print('Unknown protocol.')
    quit()


