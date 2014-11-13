import socket
import ip
from struct import *
import random
import utilities
from sets import Set
import time


'''
TCP Header
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Acknowledgment Number                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Data |           |U|A|P|R|S|F|                               |
| Offset| Reserved  |R|C|S|S|Y|I|            Window             |
|       |           |G|K|H|T|N|N|                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Checksum            |         Urgent Pointer        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options                    |    Padding    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             data                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
'''

# This is a TCP class. Each instance should handle the whole parts
# of three_ways_handshake, send_request, get_request and give back
# to application layer. REMEMBER: Each TCP instance should be binded
# to one remote host.

class Tcp(object):
    MAX_WIN_SIZE = 5840

    def __init__(self, hostname):
        self.ip = ip.Ip()
        self.src_ip = utilities.getLocalIP()
        self.dest_ip = utilities.getDestIP(hostname)
        self.src_port = random.randint(1024, 65530)
        self.dest_port = 80
        self.seq_num = random.randint(0, 65536 * 65536)
        self.ack_num = 0
        self.c_wind = 1

        # The expected packets is the lists of sent packets
        # but not yet acked. The entry is expected ack number.
        self.expected_packets = Set([])
        self.received_packets = Set([])
        self.out_of_order_packets = {}
        self.last_acked_time = time.time()

    def build_header(self, payload, first=False, isFIN = False):
        # tcp header fields
        
        # source port
        tcp_source = self.src_port
        # destination port
        tcp_dest = self.dest_port
        tcp_seq = self.seq_num
        tcp_ack_seq = self.ack_num

        #4 bit field, size of tcp header, 5 * 4 = 20 bytes
        tcp_doff = 5
        #tcp flags
        if isFIN:
            tcp_fin = 1
        else :
            tcp_fin = 0

        if first:
            tcp_syn = 1
            tcp_ack = 0
        else :
            tcp_syn = 0
            tcp_ack = 1
        tcp_rst = 0
        tcp_psh = 0
        tcp_urg = 0

        #   maximum allowed window size
        tcp_window = socket.htons(Tcp.MAX_WIN_SIZE)
        check_sum = 0
        tcp_urg_ptr = 0
         
        tcp_offset_res = (tcp_doff << 4) + 0
        tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)

        # Initial Build TCP Header.
        tcp_header = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, check_sum, tcp_urg_ptr)

        # pseudo header fields
        source_address = socket.inet_aton(self.src_ip)
        dest_address = socket.inet_aton(self.dest_ip)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_header) + len(payload)

        # Build pseudo header.
        pseudo_header = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
        msg = pseudo_header + tcp_header + payload;

        check_sum = utilities.checksum(msg)
        # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
        tcp_header = pack('!HHLLBBH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + pack('H' , check_sum) + pack('!H' , tcp_urg_ptr)

        return tcp_header

    def verify_checksum(self, raw_packet ):
        pseudo_header = pack('!4s4sBBH',
                                    socket.inet_aton(self.src_ip),
                                    socket.inet_aton(self.dest_ip),
                                    0,
                                    socket.IPPROTO_TCP,  # Protocol,
                                    len(raw_packet))

        return utilities.checksum(pseudo_header + raw_packet) == 0

    def syn(self):
        payload = ""
        # True sets syn flag to 1 and ack to 0.
        packet = self.build_header(payload, True) + payload

        self.expected_packets.add( self.seq_num + 1 )
        # The SYN packet
        self.ip.send(self.dest_ip, packet)

    def receive_syn_ack(self):
        raw_packet = self.receive()
        if self.process_raw_packet(raw_packet, True) == False:
            self.c_wind = 1
            return
        self.seq_num += 1


    def ack(self):
        payload = ""
        packet = self.build_header(payload) + payload
        # print str(time.time()) + " DEBUG: About to ack %x" % (self.ack_num)
        self.ip.send(self.dest_ip, packet)
        self.last_acked_time = time.time()

    def fin(self):
        payload = ""
        packet = self.build_header(payload, False, True) + payload

        self.ip.send(self.dest_ip, packet)



    # Set seq and ack according to raw_packet. Then generate
    # the syn/ack packet.
    def process_raw_packet(self, raw_packet, handshake = False):
        remote_seq = int(unpack("!I", raw_packet[4: 8])[0])
        fin = int(unpack("!B", raw_packet[13: 14])[0]) & 0x1
        push_flag = int(unpack("!B", raw_packet[13: 14])[0]) & 0x8
        # print "DEBUG: fin is %d" % (fin)
        if remote_seq in self.received_packets:
            print "DEBUG: Packet " + str(remote_seq) + " is duplicated."
            return False, False, fin
        if (not handshake) and (not fin) and remote_seq > self.ack_num:
            self.out_of_order_packets[ remote_seq ] = raw_packet;
            # print "DEBUG: received an out of order packet. Put in buffer."
            return False, False, fin, push_flag
        message_len = len(raw_packet) - 4 * self.header_length(raw_packet)
        if message_len == 0:
            message_len = 1

        self.ack_num = remote_seq + message_len

        self.received_packets.add(remote_seq)

        # if message_len != 1:
        #     self.result += raw_packet[-message_len : ]
        # if fin == 1:
        #     self.ack()
        #     self.fin()
        #     if push_flag:
        #         self.result += raw_packet[-message_len : ]

        # print "DEBUG: received %x, length: %d, fin is %d" % (remote_seq, message_len, fin)
        return raw_packet[-message_len : ], remote_seq, fin, push_flag
        

    # TODO check if the recv_packet is valid. ACK number, checksum.
    def is_valid(self, raw_packet):
        if not self.verify_checksum(raw_packet):
            return False
        remote_seq = int(unpack("!I", raw_packet[4:8])[0])
        remote_ack = int(unpack("!I", raw_packet[8:12])[0])
        if remote_ack in self.expected_packets:
            self.expected_packets.remove(remote_ack)
            return True
        elif remote_seq >= self.ack_num:
            # self.out_of_order_packets[ remote_seq ] = raw_packet
            return True
        else :
            # print "DEBUG: Packet %d %d is discarded." % (remote_seq, remote_ack)
            return False

    def header_length(self, raw_packet):
        return int(unpack("!B", raw_packet[12: 13])[0] / 16)

    # Three way handshake.
    def connect_to_server(self):
        self.syn()
        self.receive_syn_ack()
        self.ack()

    def process_response(self):
        self.result = ""
        while True:
            raw_packet = self.receive()
            packet, seq, fin, push_flag = self.process_raw_packet(raw_packet)
            if packet == False:
                if time.time() - self.last_acked_time > 1:
                    print "DEBUG: Time out, sending ack."
                    self.ack()
                # self.ack()
                continue
            # print "DEBUG: Fin is %d" % (fin)
            if fin == 1:
                self.ack()
                self.fin()
                if push_flag:
                    self.result += packet
                break
            else:
                self.result += packet
                self.ack()


    def send(self, payload):
        start_time = time.time()
        # First, connect to remote server.
        print "Starting three-way-handshake."
        self.connect_to_server()
        print "Finished three-way-handshake."

        print "Starting the HTTP request."
        # Then send the request.
        # print "DEBUG: HTTP request: %s" % ( payload )
        tcp_packet = self.build_header(payload) + payload
        self.ip.send(self.dest_ip, tcp_packet)

        # This is the ACK of HTTP request.
        if self.receive():
            if self.c_wind < 1000:
                self.c_wind += 1
        self.seq_num += len(payload)
        print "Finished the HTTP request."
        
        print "Getting response"
        # Then process response get get final result.
        result = self.process_response()
        print "Total time is: " + str(time.time() - start_time) + " seconds."

    def receive_result(self):
        return self.result
        

    def receive(self):
        while True:
            # Receive the ACK packet from server.
            if self.out_of_order_packets.has_key( self.ack_num ):
                # print "DEBUG: A packet is in buffer."
                return self.out_of_order_packets.pop( self.ack_num )
            try:
                recv_packet = self.ip.receive(self.dest_ip, self.src_port)
                if self.is_valid(recv_packet):
                    return recv_packet
            except TimeoutError:
                print "DEBUG: Haven't received packet for 1 seconds. Sending three acks."
                self.ack()
                self.ack()
                self.ack()
                continue
