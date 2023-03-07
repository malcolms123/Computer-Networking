
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


def ping(host, skt = None, seqno = 1, ttl = 30, quiet = False):
    # setting TTL
    skt.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    # make initial packet
    ident = random.randint(0,0xffff)
    header = struct.pack("!BBHHH",8,0,0,ident,seqno)
    send_time_ns = int(1e9 * time.time())
    payload = struct.pack("!Q", send_time_ns)
    packet = header + payload
    # checksum and recreate packet
    c = checksum(packet)
    header = struct.pack("!BBHHH",8,0,c,ident,seqno)
    packet = header + payload
    # send and receive packet
    print(f"Pinging {host} with {len(packet)} bytes and ttl = {ttl}.")
    skt.sendto(packet, (host,0))
    resp, addr = skt.recvfrom(1024)
    rx_time_ns = int(1e9 * time.time())
    # decyphering ICMP response
    icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq = struct.unpack("!BBHHH",resp[20:28])
    # checking for any inconsistencies
    assert icmp_type == 0 or icmp_type == 11, "Invalid ICMP type"
    assert icmp_code == 0, "Invalid ICMP code."
    assert icmp_id == ident or icmp_id == 0, "Invalid ICMP identifier."
    assert icmp_seq == seqno or icmp_seq == 0, "Invalid ICMP sequence number."
    local_check = checksum(resp)
    assert local_check == 0, "Failed local checksum."

    icmp_send_time = struct.unpack("!Q",resp[28:36])[0]
    rtt_ns = rx_time_ns - icmp_send_time
    rtt_ms = rtt_ns/1e6

    print(f"ICMP response: {icmp_id}, {icmp_seq}, [{local_check}], rtt = {rtt_ms} ms")
    return True, rtt_ms




		
if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("host", help="Host to ping")
	parser.add_argument("-t", "--ttl", help="Time to live", default=30, type=int)
	parser.add_argument('-n', '--num', help="Number of pings", default=3, type=int)
	args = parser.parse_args()
	
	# if doing multiple pings, you can reuse the same socket
	s = icmp_socket()
	rtts = []
	try:				
		# wrap this in a try block so we can close the socket if there is an error		
		for i in range(args.num):
			valid, rtt = ping(args.host, skt = s, seqno = i, ttl=i+1)
			if valid:	
				rtts.append(rtt)
		
	except KeyboardInterrupt:
		print("^C")
	finally:
		# close the socket when done
		s.close()

	print("---  ping statistics ---")
	print (f"{args.num} packets transmitted, {len(rtts)} packets received, {100*(args.num - len(rtts))/args.num:3.2f}% packet loss, time {sum(rtts):8.3f}ms")
	if len(rtts) > 0:		
		print (f"rtt min/avg/max = {min(rtts):6.3f}/{sum(rtts)/len(rtts):6.3f}/{max(rtts):6.3f} ms")