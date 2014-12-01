import socket
import sys
import json
import constants

# This class uses a udp socket to handle the traffic. It has the 
# following responsibilities:
# 1. Receive updates from replicas. The updates should contain the
#   RTT between that replica and all existing clients.
# 2. Receive new client from DNS server. When DNS server receives a 
#   new request, it should inform this class.
# 3. Maintain a map data structure of client: replica_ip pairs.

PROPERTIES_FILE = "MAP_PROPERTIES"

class Map:

    def __init__( self ):
        self.UDP_IP = "127.0.0.1"
        self.UDP_PORT = constants.UDP_PORT

        self.client_mappings = {}

        self.sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP

    def bind( self ):
        # try :
        self.sock.bind(( self.UDP_IP, self.UDP_PORT ))
        # f = open( PROPERTIES_FILE, 'w');
        # f.write( self.UDP_PORT )
        # except: 
        #     print "Socket is already in used."

    def addClient( self, client_ip ):
        print "received message from DNS: ", client_ip

    def updateClientList( self, client_list ):
        print "received message from replica: ", client_list

    def run( self ):
        while True:
            data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            message = json.loads( data )
            if message.has_key( constants._DNS ):
                self.addClient( message[ constants._DNS ] );
            elif message.has_key( constants._REPLICA ):
                self.updateClientList( message[ constants._REPLICA ])
            else :
                print "received message from unknow: ", message

def main(argv):
    map = Map()
    map.bind()
    map.run()

if __name__ == '__main__':
    main(sys.argv)