The project2 was finished by Zhemin Mi and Binbin Lu.

-----------------------------------------

The program uses 3 major methods: 

1. Parse the arguments and setup the server
2. Login
3. Crawl the page with BFS
4. Close the socket and exit the program

In "*Parse the arguments and setup the server*", we checked the arguments and passed it into the constuctor. Then create a socket and PrintWriter and BufferReader assoiciated with it.

In "*Login*", we first get the page "accounts/login/" and fetch the sessionid, then send a post request to server with username and password. If everthing is ok, we should get a response showing that login successful and a new cookie and sessionid will be created. 

In "*Crawl the page with BFS*", we used a Set to hold all visited pages. we used a Deque to hold all pages to be visited. We used regex matchers to check the response status to make sure the program won't terminate until have found 5 secret_flags.

-----------------------------------------

The major chanllenge was the login part. Thanks to the help of wireshark and chrome developer mode, we finally figure out how to set up the message and what to include in the headers and body. Wireshark also helped us debugging the 500 error and so on. 