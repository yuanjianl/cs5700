import constants
import json
import sys
import socket
import time
import os
import re

class Pinger:
    def __init__( self, port ):
        self.UDP_IP = constants.UDP_IP
        self.UDP_PORT = port

        self.sock = socket.socket(socket.AF_INET, # Internet 
                                socket.SOCK_DGRAM) # UDP

        # We don't want the socket to be blocked.
        self.sock.settimeout( 1 )

    # Send a "list clients" requests to map.py, wait and return
    # the client lists.
    def listAllClient( self ):
        # print "DEBUG: Asking map.py to client lists."
        try: 
            packet = json.dumps( {constants._REPLICA : 
                                            {"TYPE" : constants._LIST_CLIENTS
                                            } } )
            # print "SENDING to: " + str( self.UDP_IP ) + " " + str( self.UDP_PORT )
            self.sock.sendto( packet, ( self.UDP_IP, self.UDP_PORT ) )

            packet, addr = self.sock.recvfrom(1024)

            message = json.loads( packet )

            if message.has_key( constants._REPLICA ) and message[ constants._REPLICA ][ "TYPE" ] == constants._OK:
                return message[ constants._REPLICA ][ "CONTENT" ];
            else :
                print "ERROR: wrong message type."
                return []
        except socket.timeout:
            print "ERROR: Timeout!."

    # Ping each of the clients to measure the RTT. return the
    # dic of <client_ip, RTT>
    def pingClients( self, clients ):
        if clients == None:
            return
        result = {}
        for client in clients:
            command = "scamper -c 'ping -c 1' -i " + client + " | grep 'time='"
            outputs = os.popen( command ).read()
            print outputs
            if outputs.find( 'time=' ):
                m = re.search( 'time=([0-9]*.[0-9]*)', outputs )
                if m != None:
                    result[ client ] = float( m.group( 1 ) )
        return result

    # Wrap and send the result to map.py
    def sendPingResult( self, result ):
        try: 
            packet = json.dumps( {constants._REPLICA : 
                                            {"TYPE" : constants._UPDATE_CLIENTS, 
                                             "CONTENT": result
                                            } } )
            self.sock.sendto( packet, ( self.UDP_IP, self.UDP_PORT ) )

            packet, addr = self.sock.recvfrom(1024)

            message = json.loads( packet )

            if message.has_key( constants._REPLICA ) and message[ constants._REPLICA ][ "TYPE" ] == constants._OK:
                return;
        except socket.timeout:
            print "ERROR: Timeout!."

    def run( self ):
        while True:
            clients = self.listAllClient()

            result = self.pingClients( clients )
            print result
            
            self.sendPingResult( result )

            time.sleep( 3 )

def main(argv):
    pinger = Pinger( int( argv[ 0 ] ) )
    pinger.run()

if __name__ == '__main__':
    main(sys.argv[1:])