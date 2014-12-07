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

'''
ec2-54-164-51-70.compute-1.amazonaws.com    Origin server (running Web server on port 8080)
ec2-54-174-6-90.compute-1.amazonaws.com     N. Virginia
ec2-54-149-9-25.us-west-2.compute.amazonaws.com Oregon
ec2-54-67-86-61.us-west-1.compute.amazonaws.com N. California
ec2-54-72-167-104.eu-west-1.compute.amazonaws.com   Ireland
ec2-54-93-182-67.eu-central-1.compute.amazonaws.com Frankfurt, Germany
ec2-54-169-146-226.ap-southeast-1.compute.amazonaws.com Singapore
ec2-54-65-104-220.ap-northeast-1.compute.amazonaws.com  Tokyo, Japan
ec2-54-66-212-131.ap-southeast-2.compute.amazonaws.com  Syndey, Australia
ec2-54-94-156-232.sa-east-1.compute.amazonaws.com   Sao Paulo, Brazil
'''

replicas = ['54.174.6.90', '54.149.9.25', '54.67.86.61', 
            '54.72.167.104', '54.93.182.67', '54.169.146.226',
            '54.65.104.220', '54.66.212.131', '54.94.156.232']

DEFAULT_REPLICA = "54.94.156.232"

# Match the prefix of part1 and part2.
def match( part1, part2 ):
    bitArray1 = []
    bitArray2 = []
    for i in range( 8 ):
        base = 128 / ( 2 ** i )
        bitArray1.append( part1 / base )
        part1 = part1 % base
        bitArray2.append( part2 / base )
        part2 = part2 % base
    result = 0
    for index in range( len( bitArray1 ) ):
        if bitArray1[ index ] == bitArray2[ index ]:
            result += 1
        else :
            break
    return result

def prefixMatch( ip1, ip2 ):
    ip1 = ip1.split('.')
    ip2 = ip2.split('.')
    if len( ip1 ) !=  len( ip2 ):
        return 0
    else :
        result = 0
        for index in range( len( ip1 ) ):
            matchResult = match( int(ip1[ index ]), int(ip2[ index ]) )
            result += matchResult
            if matchResult != 8:
                break
        return result

def longestPrefixMatch( client_ip, ip_list ):
    result = -1
    result_ip = ''
    for server_ip in ip_list:
        prefixResult = prefixMatch ( client_ip, server_ip )
        if result < prefixResult:
            result = prefixResult
            result_ip = server_ip
    print "MAP.PY longest prefix match for " + client_ip + " is " + result_ip
    return result_ip

class Map:

    def __init__( self , port ):
        self.UDP_IP = socket.gethostbyname( constants.UDP_IP )
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
            replica = longestPrefixMatch( client_ip, replicas )
            self.client_mappings[ client_ip ] = [ 10000, replica ]

    def selectReplica( self, client_ip ):
        # Do whatever we need to select a best replica server
        # for the client_ip.
        print client_ip + " is requesting."
        print self.client_mappings
        if self.client_mappings.has_key( client_ip ):
            replica = self.client_mappings[ client_ip ][1]
        else :
            replica = longestPrefixMatch( client_ip, replicas )
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

    def updateClientList( self, client_list, replica_ip ):
        packet = json.dumps( {constants._REPLICA : 
                    {"TYPE" : constants._OK
                    } 
            } )

        if client_list != None:
            for client in client_list.keys():
                if self.client_mappings.has_key( client ):
                    if self.client_mappings[ client ][ 0 ] > client_list[ client ]:
                        self.client_mappings[ client ][ 0 ] = client_list[ client ]
                        self.client_mappings[ client ][ 1 ] = replica_ip
                else :
                    self.client_mappings[ client ] = [ client_list[ client ], replica_ip ]

        return packet

    def run( self ):
        while True:
            packet, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            try :
                message = json.loads( packet )
            except :
                print "message is not in json format"
                continue

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
                    packet = self.updateClientList( data[ "CONTENT" ], addr[ 0 ] )
                    self.sock.sendto( packet, addr )
            else :
                print "received message from unknow: ", message

def main(argv):
    map = Map( int(argv[0]) )
    map.bind()
    map.run()

if __name__ == '__main__':
    main(sys.argv[1:])