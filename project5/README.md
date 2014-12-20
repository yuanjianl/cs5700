####README for [Project5](http://david.choffnes.com/classes/cs4700fa14/project5.php)####

EC2 Servers
===========
ec2-54-85-79-138.compute-1.amazonaws.com   Origin server (running Web server on port 8080)
ec2-54-84-248-26.compute-1.amazonaws.com    N. Virginia
ec2-54-186-185-27.us-west-2.compute.amazonaws.com   Oregon
ec2-54-215-216-108.us-west-1.compute.amazonaws.com  N. California
ec2-54-72-143-213.eu-west-1.compute.amazonaws.com   Ireland
ec2-54-255-143-38.ap-southeast-1.compute.amazonaws.com  Singapore
ec2-54-199-204-174.ap-northeast-1.compute.amazonaws.com Tokyo
ec2-54-206-102-208.ap-southeast-2.compute.amazonaws.com Sydney
ec2-54-207-73-134.sa-east-1.compute.amazonaws.com   Sao Paulo

Milestone December 5th, 2014
=======================
High-Level Approach
1. DNS Server
Look up the format for a DNS A record query, then implement code that parses it and get the domain name that clients request. Follow the format for a DNS answer and build a DNS packet, then returns a well-formed response with a specific IP address.

2. HTTP Server
We customize our HTTP server based on python built-in HTTPServer class.

Final Project December 7th, 2014
==============================

In DNS Server and each of the replicas, there are two process running. In DNS Server,
dns.py and map.py is running. dns.py is handling all DNS request, map.py is the one
that has the information of which replica is the best for a given client ip. In 
Replica server, httpserver.py is handling all http request, and pinger.py periodically
pings the clients and pass the information to map.py in DNS server.

The CDN architecture is drawed as the following. It also has the work flow of the CDN
including the client requests.

The diagram is an ascii art. Please open it with the width of editor set to at least 90

	-------------------------------------------------------------------------------------
	|             DNS Server                  ||                 REPLICAS              |
	|      dns.py      |        map.py        ||      pinger.py       |  httpserver.py |
	|  ^  |      (2) Best replica             ||                      | |    ^  |   ^  |
	|  |  |     -------------->               ||                      | | (7)|  |(6)|  |
	|  |  |       for client A        (a) List clients    |---------| | |    |  |   |  |
	|  |  |            |             <--------------------| Measure | | |    |  |   |  |
	|  |  |            |                      ||          |  every  | | |    |  |   |  |
	|  |  |            |              (b) OK, Client List |    2    | | |    | \|/  |  |
	|  |  |      (3) Replica IP      -------------------->| seconds | | | |-------| |  |
	|  |  |     <--------------               ||          |---------| | | | cache | |  |
	|  |  |            |                      ||             ^   |    | | |  or   | |  |
	|  |  |            |                      ||             |   |    | | |origin | |  |
	|  |  |            |                      ||             |   |    | | |-------| |  |
	|  |  |            |              (e) Measuremnt         |   |    | |           |  |
	|  |  |            |             <-------------------    |   |    | |           |  |
	|  |  |            |                   Result            |   |    | |           |  |
	|  |  |            |                      ||             |   |    | |           |  |
	|  |  |            |                      ||             |   |    | |           |  |
	|  |  |            |                      ||             |   |    | |           |  |
	|  |  |            |             (f)      OK             |   |    | |           |  |
	|  |  |            |             ------------------>     |   |    | |           |  |
	|  |  |            |                      ||             |   |    | |           |  |
	|  |  |            |                      ||             |   |    | |           |  |
	|  |  |            |                      ||             |   |    | |           |  |
	|  |  |            |                      ||             |   |    | |           |  |
	|  |  |            |                      ||             |   |    | |           |  |
	|  |  |            |                      ||   (d) RTT   |   |    | |           |  |
	|  |  |                                  -----------------   |      |           |  | 
	|  |  |                                  |      (c) ping     |      |           |  | 
	|  |  |                                  |  -----------------|      |           |  | 
	|  |  |(4) DNS Response                  |  |  (8) content          |           |  | 
	|  |  |--------------------------------- |  | ----------------------|           |  |  
	|  |                                   | | \|/|                                 |  |
	|  |  (1) DNS Request                 \|/    \|/   (5) wget content from        |  | 
	|   ---------------------------------  Client A---------------------------------   |
	|                                                            Replica               |
	|                                                                                  |
	|----------------------------------------------------------------------------------|


Measurement:
We are using the active measument. Once a client has sent a DNS request to DNS server,
 the map.py will remember the ip of the client. Periodically, pinger.py in each 
replica server would get the current client list from map.py, ping each of them to 
get RTT, then sending it back. In map.py, if the new RTT is smaller than current,
 map the client to the new Replica. The reason we put the map.py to DNS server is
that we try to take advantage of no memory limit on DNS server. In replicas, we are
trying to cache as much as possible ( lesss than 10MB limit of course ).

Cache:
We are using the LFU cache replacement strategy, which keeps track of recent requested pages frequency list, and remove the least requested if exceed memory size.  


