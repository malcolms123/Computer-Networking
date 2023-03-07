
"""
A sample program to send ICMP echo requests to a host to demonstrate
how to use the socket module to send and receive ICMP messages.

This requires root privileges to run. 

Marchiori, 2023

test sites:

eg.bucknell.edu
bbc.co.uk
asahi-net.jp
google.com
yahoo.com
apple.com

"""

import argparse
import socket
import struct
import time
import random

def icmp_socket(timeout = 1, ttl = 30):
	"Create a raw socket for ICMP messages"
	s = socket.socket(
			family = socket.AF_INET, 
		    type = socket.SOCK_RAW, 
			proto = socket.getprotobyname("icmp"))
	# Set the timeout
	s.settimeout(timeout)
	# Set the TTL
	s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
	return s

def checksum(data):
	"Calculate the checksum for the data"
	sum = 0
	# make 16 bit words out of every two adjacent 8 bit words in the packet
	for i in range(0, len(data), 2):
		if i + 1 < len(data):
			sum += (data[i] << 8) + data[i+1]
		else:
			sum += data[i] << 8
	# take only 16 bits out of the 32 bit sum and add up the carries
	sum = (sum >> 16) + (sum & 0xffff)
	sum += (sum >> 16)
	
 	# one's complement
	return ~sum & 0xffff


def ping(host, skt = None, ttl = 30, quiet = False):
    # setting TTL
    skt.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    # make initial packet
    packet = struct.pack("!BBHHH",8,0,0,0,0)
    # checksum and recreate packet
    c = checksum(packet)
    packet = struct.pack("!BBHHH",8,0,c,0,0)
    # send and receive packet
    send_time = time.time()
    skt.sendto(packet, (host,0))
    try:
    	resp, addr = skt.recvfrom(1024)
    except socket.timeout:
    	print(f"{ttl}  *  *")
    	return False
    rx_time = time.time()
    # decyphering ICMP response
    icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq = struct.unpack("!BBHHH",resp[20:28])
    ip_addr = socket.inet_ntoa(struct.unpack("!4s",resp[12:16])[0])
    # checking for any inconsistencies
    assert icmp_type == 0 or icmp_type == 11, f"Invalid ICMP type: {icmp_type}"
    assert icmp_code == 0, f"Invalid ICMP code: {icmp_code}"
    local_check = checksum(resp)
    assert local_check == 0, "Failed local checksum."
    # calculating rtt
    rtt_ms = round(1e3*(rx_time-send_time),4)
    # printing results
    print(f"{ttl}  {ip_addr}  {rtt_ms} ms")
    # testing if final stop
    if icmp_type == 11:
    	return False
    else:
    	return True





		
if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("host", help="Host to ping")
	parser.add_argument('--max_hops', help="Maximum hops.", default=30, type=int)
	args = parser.parse_args()
	
	# if doing multiple pings, you can reuse the same socket
	s = icmp_socket()
	print(f"traceroute to {args.host}, {args.max_hops} hops max")
	try:				
		# wrap this in a try block so we can close the socket if there is an error		
		for i in range(args.max_hops):
			valid = ping(args.host, skt = s, ttl=i+1)
			if valid:
				print(f"{args.host} reached in {i+1} hops.")
				break
		if not valid:
			print(f"{args.host} not reached within {args.max_hops} hops.")
		
	except KeyboardInterrupt:
		print("^C")
	finally:
		# close the socket when done
		s.close()