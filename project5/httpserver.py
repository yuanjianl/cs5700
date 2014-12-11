from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse
import urllib2
import getopt
import sys
import os

# This class gives definition of double lined list node for LFU frequency list.
# @freq is used to record number of visited time,
# @paths contains all available file path in local disk
class CacheNode:
	def __init__(self, freq = 1, path = None):
		self.prev = None
		self.next = None
		self.freq = freq
		self.paths = set()
		if path is not None:
			self.paths.add(path)

# This class gives definition of LFU cache. 
# @maxSize is the max capacity of files in local disk
# @currSize is current number of files in local disk
# @map stores mapping of path of url to cache node in the frequency double linked list
# @head is the head pointer of frequency list
class LFUCache:
	def __init__(self, maxSize = 270):
		self.currSize = 0
		self.maxSize = maxSize
		self.map = {}
		self.head = None

	# Insert a url path into LFU cache
	def insert(self, path):
		if path in self.map:
			print 'Path already exists in map, no need to add'
		else: 
			# Check if current number of local url files exceed or equal to maximum size
			if self.currSize >= self.maxSize:
				while self.currSize > self.maxSize:
					self.remove()
					self.currSize -= 1
				self.remove()
			else:
				self.currSize += 1

			# Add path in cache node with frequency as 1
			if self.head is not None and self.head.freq == 1:
				self.head.paths.add(path)
			else:
				cacheNode = CacheNode(1, path)
				cacheNode.next = self.head
				if self.head is not None:
					self.head.prev = cacheNode
				self.head = cacheNode

			# Add path is map with key as path, value as head of frequency list
			self.map[path] = self.head

	# Update frequency list for input url file, increasing frequency by 1 
	def update(self, path):
		curr = self.map[path]

		if curr is None:
			print "Path doesn't have a cache node in map"
			return

		# Remove path from original cache node
		curr.paths.remove(path)

		currFreq = curr.freq
		next = curr.next
		if next is None or next != currFreq + 1:
			next = CacheNode(currFreq + 1, path)
			next.next = curr.next
			if len(curr.paths) == 0:
				next.prev = curr.prev
				curr.next = None
				curr.prev = None
			else:
				next.prev = curr
			if next.next is not None:
				next.next.prev = next
			if next.prev is not None:
				next.prev.next = next
			else: self.head = next
		
		next.paths.add(path)

		# Update cache node in map
		self.map[path] = next


	def remove(self):
		if self.head is None:
			print 'Head of frequency list is None'
		elif self.currSize < self.maxSize:
			print "Current cache size hasn't reach max cache size, no need to remove"
		else:
			# Remove path from cache node and map
			path = self.head.paths.pop()
			del self.map[path]

			# Removes current cache node if it is None after remove path
			if self.head.paths is None:
				self.head = self.head.next;
				if self.head is not None:
					self.head.prev.next = None
					self.head.prev = None

			# Remove file from local disk with the give path/file name
			filename = os.getcwd() + path
			try:
				os.remove(filename)
			except OSError:
				print "Filename doesn't exit, can't delete"
				pass

	def printLFU(self):
		print 'LFU map size: ', len(self.map)

		paths_size = 0
		runner = self.head.next
		while runner is not None:
			paths = runner.paths
			print 'LFU frequency: ', runner.freq
			for path in paths:
				paths_size += 1
				print(path),
			runner = runner.next
			print ' '
		print 'LFU map size: ', paths_size

# This class implements HTTP server 
class MyHTTPHandler(BaseHTTPRequestHandler):
	def __init__(self, cache, origin, *args):
		self.origin = origin
		self.cache = cache
		BaseHTTPRequestHandler.__init__(self, *args)

	def update_cache(self):
		# for root, dirs, files in os.walk('wiki'):
		# 	for f in files:
		# 		path = '/wiki/'+f
		# 		if path not in cache.map:
		# 			cache.insert(path)
		# cache.printLFU()

		filenum = 0
		for root, dirs, files in os.walk('wiki'):
			for f in files:
				filenum += 1
		return filenum

	def do_GET(self):
		# if self.cache.currSize < 270:
		# 	self.update_cache()

		print 'self.update_cache',self.update_cache()
		print 'currSize',self.cache.currSize
		
		# If request page in not in the cache, request the page from origin server
		if self.path not in self.cache.map:
			try:
				request = 'http://' + self.origin + ':8080' + self.path
				response = urllib2.urlopen(request)
				parse_url = urlparse(response.geturl())
				self.path = parse_url.path
			except urllib2.HTTPError as he:
				self.send_error(he.code, he.reason)
				return
			except urllib2.URLError as ue:
				self.send_error(ue.reason)
				return
			else:
				self.download_from_origin(self.path, response)
		else:
			# If requested page already exists in cache, simply update the frequency list
			cache.update(self.path)
		
		self.cache.printLFU()

		try:
			# Read cached file from local file and send back to client
			with open(os.getcwd() + self.path) as request_page:
				self.send_response(200)
				self.send_header('Content-type', 'text/plain')
				self.end_headers()
				self.wfile.write(request_page.read())
		except IOError as e:
			self.send_error(e.code, e.reason)
			print "I/O error({0}): {1}".format(e.errno, e.strerror)
		except:
			print "Unexpected error:", sys.exc_info()[0]
			raise

	# Write the page from origin server into local disk
	def download_from_origin(self, path, response):
		filename = os.getcwd() + self.path
		directory = os.path.dirname(filename)
		
		if not os.path.exists(directory):
			try:
				os.makedirs(directory)
			except:
				print "Can not make dir, exceed memory size limit"

		try:
			# Handle write exception
			f = open(filename, 'w')
			f.write(response.read())

			if self.path not in self.cache.map:
				# Insert the new path in LFU cache 
				cache.insert(self.path)
		except IOError as ue:
			print 'Can not write, Wiki folder exceed memory size limit'
		
# Handle input for port number and url for origin server
def get_information(argv):
	if (len(argv) != 5):
		sys.exit('Usage: %s -p <port> -o <origin>' % argv[0])

	(port_num, origin) = (0, '')
	options, arguments = getopt.getopt(argv[1:], 'p:o:')
	for opt, arg in options:
		if opt == '-p':
			port_num = int(arg)
		elif opt == '-o':
			origin = arg
		else: 
			sys.exit('Usage: %s -p <port> -o <origin>' % argv[0])
	return port_num, origin

# def initialize_cache(cache, map):
# 	while cache.currSize < cache.maxSize - 10:
# 		try:
# 			request = 'http://ec2-54-164-51-70.compute-1.amazonaws.com:8080/wiki/Special:Random'
# 			response = urllib2.urlopen(request)
# 			parse_url = urlparse(response.geturl())
# 			path = parse_url.path
# 		except:
# 			print "Unexpected error:", sys.exc_info()[0]
# 			print 'Sub process ended'
# 			break
# 		else:
# 			filename = os.getcwd() + path
# 			directory = os.path.dirname(filename)
		
# 			if not os.path.exists(directory):
# 				try:
# 					os.makedirs(directory)
# 				except:
# 					print "Can not make dir, exceed memory size limit"
# 					break

# 			try:
# 				# Handle write exception
# 				f = open(filename, 'w')
# 				f.write(response.read())

# 				if path not in cache.map:
# 					# Insert the new path in LFU cache 
# 					cache.insert(path)
# 			except IOError as ue:
# 				print 'Can not write, Wiki folder exceed memory size limit'
# 				break
# 		cache.printLFU()

# def start_server(cache, port_num, origin):
# 	def handler(*args):
# 		MyHTTPHandler(cache, origin, *args)
# 	httpserver = HTTPServer(('', port_num), handler)
# 	httpserver.serve_forever()



# Read from local disk, which caontains files randomly downloaded before, to initialize cache
def initialize_cache():
	cache = LFUCache(maxSize = 270)
	for root, dirs, files in os.walk('wiki'):
		for f in files:
			cache.insert('/wiki/'+f)
	# cache.printLFU()
	return cache

if __name__ == '__main__':
	(port_num, origin) = get_information(sys.argv)

	# Initialize cache here
	cache = initialize_cache()
	def handler(*args):
		MyHTTPHandler(cache, origin, *args)
	httpserver = HTTPServer(('', port_num), handler)
	httpserver.serve_forever()

	# t1 = Process(target=initialize_cache, args = (cache,))
	# t2 = Process(target=start_server, args = (cache, port_num, origin))
	# t1.daemon = True
	# t2.daemon = True
	# t1.start()
	# t2.start()
	# t1.join()
	# t2.join()

	# p = Process(target=initialize_cache, args = (cache,))
	# p.start()
	# p.join()




	

    



