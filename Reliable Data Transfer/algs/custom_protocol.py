
import logging
import binascii
import time
import socket
import math
import os.path
import os
from algs.utils import load_file
from algs.udp_wrapper import UdpWrapper
from algs.texcept import TransferFailed


from datetime import datetime, timedelta

log = logging.getLogger(__name__)

class CustomProtocol:
    def __init__(self, retries=8):
        self.retries = retries
        self.timeout = timedelta(seconds=5)

    def run_server(self, outdir, addr, mtu):
        "run the server on the given addr/port/mtu, files are stored in outdir"
        # make sure directory exists
        os.makedirs(outdir, exist_ok=True)
        mtu = mtu + 8

        # create the socket to listen on
        sock = UdpWrapper(addr)

        # use blocking on the server.
        sock.setblocking(True)

        counter = 0

        # bind the socket to the (address, port)
        sock.bind(addr)
        in_xfr = False
        outfile = None
        last = datetime.now() - self.timeout

        log.info("Server started on {}".format(addr))
        while True:
            # wait for some data to arrive
            data,remote_addr = sock.recvfrom(mtu)

            ahead = []

            for a in ahead:
                fsn = int.from_bytes(a[:4],byteorder='little')
                if fsn == counter:
                    outfile.write(a[8:])
                    counter += 1

            #print('expecting ' + str(counter))
            #print('got ' + str(int.from_bytes(data[:4],byteorder='little')))

            if in_xfr and datetime.now() - last > self.timeout:
                # we got something but it's been too long, abort
                log.info("Abort transfer due to timeout.".format())
                in_xfr = False
                if outfile:
                    outfile.close()
                    outfile = None

            if in_xfr:
                # we are in a transfer, check for end of file
                if data[:9] == B"///END\\\\\\":
                    log.info("Done receiving file from {}.".format(
                        filepath, remote_addr))
                    in_xfr = False
                    outfile.close()
                    outfile = None
                    # let the client know we are done (ack the END message)
                    sock.sendto(B"OKEND", remote_addr)
                elif data[:5] == B'BEGIN':
                    sock.sendto(B'OKBEGIN', remote_addr)
                else:
                    seq_num = int.from_bytes(data[:4],byteorder='little')
                    if seq_num < counter:
                        log.debug("Previously received sequence number. Acking.")
                        st = 'ACK' + str(seq_num)
                        sock.sendto(st.encode('utf-8'), remote_addr)
                    elif seq_num > counter:
                        found = False
                        for a in ahead:
                            fsn = int.from_bytes(a[:4],byteorder='little')
                            if fsn == seq_num:
                                found = True
                        if found:
                            log.debug("Future sequence nubmer. Ignoring.")
                        elif not found:
                            log.debug("Future sequence number. Saving.")
                            ahead.append(data)
                    elif data[4:8] == binascii.crc32(data[8:]).to_bytes(4, byteorder='little'):
                        # else we got a chunk of data
                        log.debug("Got a chunk with valid checksum!")
                        
                        # just write the data...
                        outfile.write(data[8:])
                        st = 'ACK' + str(seq_num)
                        # and send an ack
                        sock.sendto(st.encode('utf-8'), remote_addr)
                        counter += 1
                    else:
                        log.debug("checksum failed!")
                        sock.sendto(B'NACK', remote_addr)
            else:
                # we are not in a transfer, check for begin
                if data[:5] == B'BEGIN':
                    # parse the message to get mtu and filename
                    smsg = data.decode('utf-8').split('\n')
                    beginmsg = smsg[0]
                    filename = smsg[1]
                    filepath = os.path.join(outdir, filename)
                    counter = 0

                    # check mtu
                    remote_mtu= int(beginmsg.split("/")[1])
                    if remote_mtu > mtu:
                        log.error("Cannot receive {} from {}, MTU({}) is too large.".format(
                            filepath, remote_addr, remote_mtu))
                        # send an error to the client
                        sock.sentdo(B'ERROR_MTU', remote_addr)
                    else:
                        log.info("Begin receiving file {} from {}.".format(
                            filepath, remote_addr))
                        outfile = open(filepath, 'wb')
                        in_xfr = True
                        # ack the begin message to the client
                        sock.sendto(B'OKBEGIN', remote_addr)
                else:
                    # we got something unexpected, ignore it.
                    #print(data)
                    log.info("Ignoreing junk, not in xfer.")
                    if data[:9] == B"///END\\\\\\":
                        sock.sendto(B"OKEND", remote_addr)
            last = datetime.now()

    def begin_xfr(self, dest, filename, mtu):
        # create a socket to the destination (addr, port)
        sock = UdpWrapper(dest)

        #strip any path chars from filename for security
        filename = os.path.basename(filename)

        # timeout on recv after 1 second.
        sock.settimeout(1)
        tries = 0

        # retry until we get a response or run out of retries.
        while tries < self.retries:
            # construct the BEGIN message with MTU and filename
            msg = "BEGIN/{}\n{}".format(mtu, filename).encode('utf-8')

            # send the message
            sock.sendto(msg, dest)
            try:
                # wait for a response
                data, addr = sock.recvfrom(mtu)
            except socket.timeout:
                log.info("No response to BEGIN message, RETRY")
                tries += 1
                continue
            break
        # if we ran out of retries, raise an exception.
        if (tries >= self.retries):
            raise TransferFailed("No response to BEGIN message.")

        # if we got a response, make sure it's the right one.
        if data != B"OKBEGIN":
            raise TransferFailed("Bad BEGIN response from server, got {}".format(
                data
            ))

        # return the socket so we can use it for the rest of the transfer.
        return sock

    def end_xfr(self, sock, dest, mtu):
        # send the END message
        tries = 0
        while tries < self.retries:
            # send the message
            sock.sendto(B"///END\\\\\\", dest)
            try:
                # wait for a response
                data, addr = sock.recvfrom(mtu)
            except socket.timeout:
                log.info("No response to END message, RETRY")
                tries += 1
                continue
            break
        if (tries >= self.retries):
            raise TransferFailed("No response to END message.")
        # if we got a response, make sure it's the right one.
        if data != B"OKEND":
            raise TransferFailed("Bad END response from server, got {}".format(
                data
            ))

    def xfr(self, sock, payload, dest, mtu):
        # setting default rtt
        recent_rtt = [0.1,0.1,0.1,0.1,0.1]
        # send each chunk, waiting for an ACK
        sent=False
        for i,chunk in enumerate(payload):
            tries = 0
            log.info("Send chunk {} of {}".format(i, len(payload)-1))
            while tries < self.retries:


                checksum = binascii.crc32(chunk).to_bytes(4, byteorder='little')

                chunk1 = i.to_bytes(4, byteorder='little') + checksum + chunk
                
                #print('sending ' + str(i))


                # send the chunk
                if not sent:
                    sock.sendto(chunk1, dest)
                    sent = True
                sent = time.time()
                try:
                    # wait for an ACK or NACK
                    data, addr = sock.recvfrom(mtu)
                except socket.timeout:
                    log.info("No response to CHUNK message, RETRY")
                    sent = False
                    tries += 1
                    continue
                # got a response so time the rtt
                if data[:3] == B'ACK':
                    if data.decode('utf-8') == 'ACK' + str(i):
                        received = time.time()
                        diff = received-sent
                        recent_rtt.pop(0)
                        recent_rtt.append(diff)
                        avg_rtt = sum(recent_rtt)/len(recent_rtt)
                        sock.settimeout(4*avg_rtt)
                        #print('ack received')
                        sent = False
                        data = None
                        break
                    elif int(data.decode('utf-8')[3:]) < i:
                        log.info('Duped packet ACK. Not retrying')
                        #print(data.decode('utf-8')[3:])
                else:
                    log.info("Bad response from server, got {} instead of ACK{}, RETRY".format(
                        data,i))
                    sent = False
            if (tries >= self.retries):
                raise TransferFailed("No response to CHUNK message.")

    def chunk(self, payload, mtu):
        "break a payload into mtu sized chunks"
        # simple chunking by MTU
        chunks = math.ceil(len(payload) / mtu)
        return [payload[i*mtu:(i+1)*mtu] for i in range(chunks)], len(payload)

    def send_file(self, filename, dest, mtu):
        "Entrypoint for stop and wait sending"
        st = datetime.now()
        log.info("Sending with custom protocol {} --> {}:{} [MTU={}].".format(
            filename, dest[0], dest[1], mtu))

        # break the file into mtu sized pieces
        payload, total_bytes = self.chunk(load_file(filename), mtu)

        # begin the transfer
        s = self.begin_xfr(dest, filename, mtu)

        # send the chunks
        self.xfr(s, payload, dest, mtu)
        s.settimeout(1)

        # end the transfer
        self.end_xfr(s, dest, mtu)

        # print stats
        et = datetime.now()
        seconds = (et-st).total_seconds()
        log.info("Sent with custom protocol {} in {} seconds = {:.0f} bps.".format(
            filename, seconds,
            total_bytes / seconds))

        return True

# singleton
custom = CustomProtocol()
