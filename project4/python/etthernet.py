import binascii
import socket
from struct import *
import sys

import utilities


ARPOP_REQUEST = 1
ARPOP_REPLY = 2


class Ethernet:

    def __init__(self):
        #create a raw socket
        try :
            self.send_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
            self.recv_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))
            self.send_sock.bind((utilities.INTERFACE, 0))
            self.recv_sock.setblocking(0)

            self.local_mac = utilities.getLocalMac()
            gateway_ip = utilities.getGateway()
            self.gateway_mac = self.find_mac(gateway_ip)
            self.dest_mac = self.gateway_mac
        except socket.error , msg:
            print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

    def build_header(self, src, dest, etther_type=0x800):
        frame_header = pack('!6s6sH',
                            binascii.unhexlify(dest),
                            binascii.unhexlify(src),
                            etther_type)
        return frame_header

    def send(self, data):
        packet = self.build_header(self.local_mac, self.dest_mac) + data

        self.send_sock.send(packet)

    def recv(self):
        while True:
            raw_packet = self.recv_sock.recv(65536)
            [dest_mac] = unpack('!6s', raw_packet[:6])
            dest_mac = binascii.hexlify(dest_mac)
            if dest_mac == self.local_mac:
                return raw_packet[14:]

    def build_arp_request(self, dest_ip):
        request = pack('!HHBBH6s4s6s4s',
                            0x0001,  # ethernet
                            0x0800,  # ip arp resolution
                            6,       # len(Mac Address)
                            4,       # len(IP Address)
                            ARPOP_REQUEST,
                            binascii.unhexlify(self.local_mac),
                            socket.inet_aton(utilities.getLocalIP()),
                            binascii.unhexlify('000000000000'),
                            socket.inet_aton(dest_ip))
        return request

    def find_mac(self, dest_ip):
        etther_type = 0x0806
        send_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        recv_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(etther_type))
        recv_sock.settimeout(1)

        self.src_mac = utilities.getLocalMac()
        src_ip = utilities.getLocalIP()

        broadcast_address = 'ffffffffffff'
        packet = self.build_header(self.local_mac, broadcast_address, etther_type) + self.build_arp_request(dest_ip)
        send_sock.sendto(packet, (utilities.INTERFACE, 0))

        while True:
            raw_packet = recv_sock.recv(4096)
            [dest_mac] = unpack('!6s', raw_packet[:6])
            dest_mac = binascii.hexlify(dest_mac)
            if dest_mac == self.src_mac:

                [result_src_mac,
                 result_src_ip,
                 result_dest_mac,
                 result_dest_ip] = unpack('!6s4s6s4s', raw_packet[14:][8:28])
                result_src_ip = socket.inet_ntoa(result_src_ip)
                result_dest_ip = socket.inet_ntoa(result_dest_ip)
                if result_src_ip == dest_ip and result_dest_ip == src_ip:
                    break

        send_sock.close()
        recv_sock.close()
        return binascii.hexlify(result_src_mac)

