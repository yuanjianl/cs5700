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

DEFAULT_REPLICA = "54.174.6.90"

class Map:

    def __init__( self , port ):
        self.UDP_IP = constants.UDP_IP
        self.UDP_PORT = port

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
        if not self.client_mappings.has_key( client_ip ):
            # TODO Actually, should use longest prefix match maybe?
            self.client_mappings[ client_ip ] = DEFAULT_REPLICA

    def selectReplica( self, client_ip ):
        # Do whatever we need to select a best replica server
        # for the client_ip.
        if self.client_mappings.has_key( client_ip ):
            replica = self.client_mappings[ client_ip ]
        else :
            replica = DEFAULT_REPLICA
        packet = json.dumps( {constants._DNS : 
                                    {"TYPE" : constants._OK, 
                                     "CONTENT": replica
                                    } 
                            } )

        return packet

    def listClients( self ):
        # print "PREPARING to list clients."
        clients = self.client_mappings.keys()
        packet = json.dumps( {constants._REPLICA : 
                            {"TYPE" : constants._OK, 
                             "CONTENT": clients
                            } 
                    } )
        return packet

    def updateClientList( self, client_list ):
        print "received message from replica: ", client_list

    def run( self ):
        while True:
            packet, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            message = json.loads( packet )

            if message.has_key( constants._DNS ):
                data = message[ constants._DNS ]
                if data[ "TYPE" ] == constants._PUT_CLIENT:
                    self.addClient( data[ "CONTENT" ] )
                elif data[ "TYPE" ] == constants._GET_REPLICA:
                    packet = self.selectReplica( data[ "CONTENT" ] )
                    self.sock.sendto( packet, addr )
            elif message.has_key( constants._REPLICA ):
                # print "RECEIVING message from Replica."
                data = message[ constants._REPLICA ]
                if data[ "TYPE" ] == constants._LIST_CLIENTS:
                    packet = self.listClients()
                    self.sock.sendto( packet, addr )
                elif data[ "TYPE" ] == constants._UPDATE_CLIENTS:
                    packet = self.updateClientList( data[ "CONTENT" ] )
                    self.sock.sendto( packet, addr )
            else :
                print "received message from unknow: ", message

def main(argv):
    map = Map( int(argv[0]) )
    map.bind()
    map.run()

if __name__ == '__main__':
    main(sys.argv[1:])