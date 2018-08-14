#!/usr/bin/python
import urllib2
import sys
import socket
import os
import re

socket.setdefaulttimeout(15)

dataTypesToDownload = [".jpg", ".jpeg", ".png", ".gif", ".ico", ".css", ".js", ".html"]

if len(sys.argv) == 1:
	url = raw_input("URL of site to clone: ")
else:
	url = sys.argv[1]

if len(sys.argv) == 2:
        pathbase = raw_input("Directory name of site where to clone it: ")
else:
        pathbase = sys.argv[2]

if "http://" not in url and "https://" not in url:
	url = "http://"+url

try:
	os.mkdir(pathbase)
except OSError:
	pass
file = open(pathbase + "/index.html", "w")
try:
	content = urllib2.urlopen(url).read()
except urllib2.URLError as e:
	print "An error occured: " + str(e.reason)
	exit()

resources = re.split("=\"|='", content)

first = False
for resource in resources:
	if first == False:
		first = True
		continue
	resource = re.split("\"|'", resource)[0]
	if any(s in resource for s in dataTypesToDownload):
		print "Downloading " + resource
		try:
			path = resource.split("/")
			
			if len(path) != 1:
				path.pop(len(path) - 1)
				trail = "./" + pathbase + "/"
				for folder in path:
					trail += folder+"/"
					try:
						os.mkdir(trail)
					except OSError:
						pass	
		except IOError:
			pass
		try:
			if "?" in resource:
				download = open(pathbase + "/"+resource.split("?")[len(resource.split("?")) - 2], "w")
			else:
				download = open(pathbase + "/"+resource, "w")
			print url+"/"+resource
			dContent = urllib2.urlopen(url+"/"+resource).read()
		except urllib2.URLError as e:
			print "An error occured: " + str(e.reason)
			download.close()
			continue
		except IOError:
			pass
			continue
		download.write(dContent)
		download.close()
		print "Downloaded!"

file.write(content)

print "Cloned "+url+" !"

file.close()
