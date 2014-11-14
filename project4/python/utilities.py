import socket
import struct
import fcntl
import commands

INTERFACE = 'eth1'

# checksum functions needed for calculation checksum
def checksum(msg):
    if len(msg) % 2 == 1:  # the length of msg in bytes is an odd number
        msg += struct.pack('B', 0)
    s = 0
    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
        s += w
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    # complement and mask to 4 byte short
    s = ~s & 0xffff
    return s

# Return the ip address of localhost. Use ifconfig.
def getLocalIP(interface=INTERFACE):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(sock.fileno(),
                                        0x8915, struct.pack('256s', interface[:15]))[20:24])

def getLocalMac(interface=INTERFACE):
    mac_address = commands.getoutput("ifconfig " + interface + " | grep HWaddr | awk '{ print $5 }'")
    if len( mac_address ) == 17:
        return mac_address.replace(':', '')

def getGateway():
    lines = commands.getoutput('route -n').split('\n')
    for line in lines:
        record = line.split()
        if record[0] == '0.0.0.0':
            return record[1]

def getDestIP(hostname):
    return socket.gethostbyname(hostname)

def ip_to_tuple(ip_address):
    result = ip_address.split(".")
    return tuple([int(x) for x in result])


