# This class uses a udp socket to handle the traffic. It has the 
# following responsibilities:
# 1. Receive updates from replicas. The updates should contain the
#   RTT between that replica and all existing clients.
# 2. Receive new client from DNS server. When DNS server receives a 
#   new request, it should inform this class.
# 3. Maintain a map data structure of client: replica_ip pairs.

