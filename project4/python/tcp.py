import socket
import ip
from struct import *
import random
import utilities


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

    def __init__(self):
        self.ip = ip.Ip()
        self.src_ip = utilities.getLocalIP()
        self.src_port = random.randint(1024, 65530)
        self.dest_port = 80
        self.seq_num = random.randint(0, 65536 * 65536)
        self.ack_num = 0
        self.c_wind = 1

    def bind_remote_host(self, hostname):
        self.dest_ip = utilities.getDestIP(hostname)

    def build_header(self, payload, first=False):
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

        self.seq_num += len(payload)
        return tcp_header

    # Set seq and ack according to raw_packet. Then generate
    # the syn/ack packet.
    def process_raw_packet(self, raw_packet):
        remote_seq = int(unpack("!I", raw_packet[4: 8])[0])
        message_len = len(raw_packet) - 4 * self.header_length(raw_packet)
        if message_len == 0:
            message_len = 1

        self.ack_num = remote_seq + message_len

        return raw_packet[-message_len : ]
        

    # TODO check if the recv_packet is valid.
    def is_valid(self, raw_packet):
        remote_ack = int(unpack("!I", raw_packet[8:12])[0])
        return True

    def header_length(self, raw_packet):
        return int(unpack("!B", raw_packet[12: 13])[0] / 16)

    # Three way handshake.
    def connect_to_server(self, hostname):
        payload = ""
        packet = self.build_header(payload, True) + payload

        # The SYN packet
        self.ip.send(hostname, packet)
        
        self.receive(hostname)
        self.seq_num += 1

        payload = ""
        packet = self.build_header(payload) + payload

        # Finish the three-way-handshake.
        self.ip.send(hostname, packet)

    def process_response(self, hostname):
        self.result = ""
        while True:
            self.result += self.receive(hostname)
            payload = ""
            packet = self.build_header(payload) + payload
            self.ip.send(hostname, packet)
            print self.result


    def send(self, payload, hostname):
        # First, connect to remote server.
        self.connect_to_server(hostname)
        
        # Then send the request.
        tcp_packet = self.build_header(payload) + payload
        self.ip.send(hostname, tcp_packet)

        # Then process response get get final result.
        result = self.process_response(hostname)

    def receive_result(self):
        pass
        

    def receive(self, hostname):
        while True:
            # Receive the ACK packet from server.
            recv_packet = self.ip.receive(hostname, self.src_port)
            if self.is_valid(recv_packet):
                return self.process_raw_packet(recv_packet)
