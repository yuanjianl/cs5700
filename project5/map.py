import socket

# This class uses a udp socket to handle the traffic. It has the 
# following responsibilities:
# 1. Receive updates from replicas. The updates should contain the
#   RTT between that replica and all existing clients.
# 2. Receive new client from DNS server. When DNS server receives a 
#   new request, it should inform this class.
# 3. Maintain a map data structure of client: replica_ip pairs.

PROPERTIES_FILE = "MAP_PROPERTIES"

class Map:
    self.UDP_IP = "127.0.0.1"
    self.UDP_PORT = 55555

    def __init__:
        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP

    def bind():
        try :
            sock.bind((UDP_IP, UDP_PORT))
            # f = open( PROPERTIES_FILE, 'w');
            # f.write( self.UDP_PORT )
        except: 
            print "Socket is already in used."

    def run:
        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            print "received message:", data

def main(argv):
    map = Map()
    map.bind()
    map.run()

if __name__ == '__main__':
    main(sys.argv)