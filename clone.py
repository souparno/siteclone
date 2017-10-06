#!/usr/bin/python
import urllib2
import sys
import socket

socket.setdefaulttimeout(10)

if len(sys.argv) == 1:
	url = raw_input("URL of site to clone: ")
else:
	url = sys.argv[1]

if "http://" not in url:
	url = "http://"+url


file = open("index.html", "w")
try:
	content = urllib2.urlopen(url).read()
except urllib2.URLError as e:
	print "An error occured: " + str(e.reason)
	exit()

content = content.replace("=\"/", "=\""+url+"/")

file.write(content)

print "Cloned "+url+" !"

file.close()