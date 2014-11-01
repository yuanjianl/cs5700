import socket

# checksum functions needed for calculation checksum
def checksum(msg):
    s = 0
 
    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        s = s + w
     
    s = (s>>16) + (s & 0xffff);
    s = s + (s >> 16);
     
    #complement and mask to 4 byte short
    s = ~s & 0xffff
     
    return s

# Return the ip address of localhost. Use ifconfig.
def getLocalIP():
    return "10.0.3.15"

def getDestIP(hostname):
    return socket.gethostbyname(hostname)

def ip_to_tuple(ip_address):
    result = ip_address.split(".")
    return tuple([int(x) for x in result])