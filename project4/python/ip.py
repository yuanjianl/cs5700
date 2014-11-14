import socket
import sys
from struct import *
import utilities
import tcp
import random
import time
from etthernet import Ethernet

'''
IP HEADER
0                   1                   2                   3   
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version|  IHL  |Type of Service|          Total Length         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Identification        |Flags|      Fragment Offset    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Time to Live |    Protocol   |         Header Checksum       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Source Address                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Destination Address                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options                    |    Padding    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
'''

class Ip(object):
    

    def __init__(self):
        #create a raw socket
        try:
            # self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            # self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            # 
            self.sock = Ethernet()
            # 
            self.local_ip = utilities.getLocalIP()

            # The TCP list that has sent from this instance. The
            # close in tcp instance should delete itself from
            # this list.
            self.tcp_list = {}
        except socket.error , msg:
            print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()


    def build_header(self, dest_ip, tcp_packet):
        # ip header fields
        ip_ihl = 5
        ip_ver = 4
        ip_tos = 0
        # If we don't overrite etthernet, kernel will fill the 
        # correct total length
        ip_tot_len = 20 + len( tcp_packet )
        ip_id = random.randint(0, 65534)   #Id of this packet
        # ip_id = 12345
        ip_frag_off = 16384
        ip_ttl = 255
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0    # kernel will fill the correct checksum
        ip_saddr = socket.inet_aton(self.local_ip)
        ip_daddr = socket.inet_aton(dest_ip)
         
        ip_ihl_ver = (ip_ver << 4) + ip_ihl

        # the ! in the pack format string means we don't care about 
        # what network order it is using. 
        ip_header = pack('!BBHHHBBH4s4s' , ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)

        ip_check = utilities.checksum( ip_header )
        ip_check = pack('H', ip_check)
        ip_header = pack('!BBHHHBB' , ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto) + ip_check + pack('!4s4s', ip_saddr, ip_daddr)
        return ip_header


    def send(self, dest_ip, tcp_packet):
        ip_header = self.build_header(dest_ip, tcp_packet)
        ip_packet = ip_header + tcp_packet
        
        # self.send_sock.sendto(ip_packet, ( dest_ip , 0 )) 
        self.sock.send( ip_packet )

    def raw_to_tcp_packet(self, raw_packet):
        return raw_packet[20:]

    def receive(self, dest_ip, tcp_port):
        start_time = time.time()
        while True:
            if time.time() - start_time > 2:
                raise socket.timeout
            # raw_packet = self.recv_sock.recv(4096)
            try :
                raw_packet = self.sock.recv()
            except :
                continue
            packet_dest_ip = unpack('!BBBB', raw_packet[16: 20])
            src_ip = utilities.ip_to_tuple(self.local_ip)
            if src_ip == packet_dest_ip:
                packet_src_ip = unpack('!BBBB', raw_packet[12:16])
                # Check if the packet is from remote host.
                # print "In ip: "
                # print dest_ip
                if not isinstance(dest_ip, tuple):
                    dest_ip = utilities.ip_to_tuple(dest_ip)
                if packet_src_ip == dest_ip:
                    port = unpack('!H', raw_packet[22: 24])[0]
                    # print port
                    if tcp_port == int(port):
                        # TODO: Should also check the checksum and so on of IP header
                        return self.raw_to_tcp_packet(raw_packet)



        