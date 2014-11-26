import sys
import SocketServer
import struct
import socket

class Packet():
    def buildPacket( self, ip ):
        self.an_count = 1
        self.flags = 0x8180

        header = struct.pack('>HHHHHH', self.id, self.flags,
                             self.qd_count, self.an_count,
                             self.ns_count, self.ar_count)

        query = ''.join(chr(len(x)) + x for x in self.q_name.split('.'))
        query += '\x00'  # add end symbol
        query_part =  query + struct.pack('>HH', self.q_type, self.q_class)

        an_name = 0xC00C
        an_type = 0x0001
        an_class = 0x0001
        an_ttl = 60  # time to live
        an_len = 4
        answer_part = struct.pack( '>HHHLH4s', an_name, an_type, an_class,
                          an_ttl, an_len, socket.inet_aton( ip ) );

        packet = header + query_part + answer_part

        return packet

    def unpackPacket( self, data ):
        [self.id,
        self.flags,
        self.qd_count,
        self.an_count,
        self.ns_count,
        self.ar_count] = struct.unpack('>HHHHHH', data[ :12 ])

        query_data = data[ 12: ]
        [self.q_type, self.q_class] = struct.unpack('>HH', query_data[-4:])
        s = query_data[:-4]
        ptr = 0
        temp = []
        while True:
            count = ord( s[ ptr ] )
            if count == 0:
                break
            ptr += 1
            temp.append(s[ ptr:ptr + count])
            ptr += count
        self.q_name = '.'.join(temp)
        print "DEBUG: " + self.q_name

class MyDNSHandler(SocketServer.BaseRequestHandler):
    """
    The DNSHandler class for our server.
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        data = self.request[0].strip()
        sock = self.request[1]

        packet = Packet()
        packet.unpackPacket(data)
        
        if packet.q_type == 1 and packet.q_name == self.server.name:
            print "DEBUG: Should reply to: " + str(self.client_address)
            ip = select_best_replica( self.client_address )
            response = packet.buildPacket( ip )

            sock.sendto(response, self.client_address)

def select_best_replica( client_address ):
    return "54.174.6.90"


class DNSServer( SocketServer.UDPServer ):
    def __init__( self, name, port, handler = MyDNSHandler):
        self.name = name
        SocketServer.UDPServer.__init__(self, ( '', port ), handler)
        return

def getPortAndName( argv ):
    if len( argv ) != 5 or argv[ 1 ] != "-p" or argv[ 3 ] != "-n":
        sys.exit( "Usage: ./dnsserver -p [port] -s [name]" )
    port = int( argv[ 2 ] )
    name = argv[ 4 ]

    return port, name

def main(argv):
    port, name = getPortAndName( argv )
    dns_server = DNSServer( name, port )
    dns_server.serve_forever()

if __name__ == '__main__':
    main(sys.argv)