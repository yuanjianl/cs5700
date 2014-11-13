import sys
import re
import tcp


URL_REGEX = "^(.*:)//([a-z\-.]+)(:[0-9]+)?(.*)$"

class Http(object):

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
        header += "User-Agent: Wget/1.13.4(linux-gnu)\n"
        header += "\n"
        return header, host
        

    def sendRequest(self, url):
        header, hostname = self.constructGetRequest(url)
        self.tcp = tcp.Tcp(hostname)
        self.tcp.send(header)

    def receiveResponse(self):
        response = self.tcp.receive_result()
        status = response.split("\n")[0]
        if "200" in status:
            index = response.find("\n\r")
            return response[index + 3 : ]
        else:
            print "Wrong status code. Abandoned request."
            return ""

    def write_to_file(self, filename, lines):
        file = open(filename, "w+")
        file.writelines(lines)
        file.close()

def main(argv):
    url = argv[0]
    http = Http()
    filename = http.getFilename(url)
    http.sendRequest(url)
    response = http.receiveResponse()
    http.write_to_file(filename, response)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: rawhttpget.py [url]"
    else :
        main(sys.argv[1:])