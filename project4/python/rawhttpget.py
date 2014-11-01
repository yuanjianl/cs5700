import sys
import re
import tcp

URL_REGEX = "^(.*:)//([a-z\-.]+)(:[0-9]+)?(.*)$"

class Http(object):
    def __init__(self):
        self.tcp = tcp.Tcp()

    # Return the filename for saving on disk.
    def getFilename(self, url):
        # Use index.html if ends with '/' or doesn't have path at all. 
        # Otherwise use the name after last '/'
        if url.count("/") == 2 or url.rfind("/") == len(url) - 1:
            return "index.html"
        else:
            return url.split("/")[-1]

    def getHostName(self, url):
        # if url.find("http://") == 0:
        #     return url.split("/")[2]
        # else:
        #     return url.split("/")[0]
        m = re.search(URL_REGEX, url)
        return m.group(2)

    def getPath(self, url):
        m = re.search(URL_REGEX, url)
        return m.group(4)


    def constructGetRequest(self, url):
        host = self.getHostName(url)
        path = self.getPath(url)
        header = ""
        header += "GET " + path + " HTTP/1.1\n"
        header += "Host: " + host + "\n"
        header += "Connection: keep-alive\n"
        header += "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36\n"
        header += "\n"
        return header, host
        

    def sendRequest(self, url):
        header, hostname = self.constructGetRequest(url)
        self.tcp.bind_remote_host(hostname)
        self.tcp.send(header, hostname)

    def receiveResponse(self):
        response = self.tcp.receive_result()
        print response

def main(argv):
    url = argv[0]
    http = Http()
    filename = http.getFilename(url)
    http.sendRequest(url)
    http.receiveResponse()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: rawhttpget.py [url]"
    else :
        main(sys.argv[1:])