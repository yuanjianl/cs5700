from urlparse import urlparse
import urllib2
import sys
import os

def update_cache():
	filenum = 0
	for root, dirs, files in os.walk('wiki'):
		for f in files:
			filenum += 1
	return filenum

def initialize_cache():
	while update_cache() < 250:
		try:
			request = 'http://54.164.51.70:8080/wiki/Special:Random'
			response = urllib2.urlopen(request)
			parse_url = urlparse(response.geturl())
			path = parse_url.path
			print 'path', path
		except urllib2.URLError as ue:
			print 'ue',ue
			print 'Sub process ended'
			break
		else:
			filename = os.getcwd() + path
			directory = os.path.dirname(filename)
		
			if not os.path.exists(directory):
				try:
					os.makedirs(directory)
				except:
					print "Can not make dir, exceed memory size limit"
					break

			try:
				# Handle write exception
				f = open(filename, 'w')
				f.write(response.read())
			except IOError as ue:
				print 'Can not write, Wiki folder exceed memory size limit'
				break

if __name__ == '__main__':
	# request = 'http://ec2-54-164-51-70.compute-1.amazonaws.com:8080/wiki/Special:Random'
	# response = urllib2.urlopen(request)
	# parse_url = urlparse(response.geturl())
	# path = parse_url.path
	# print response.read()
	initialize_cache()
	