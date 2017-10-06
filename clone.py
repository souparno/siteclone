#!/usr/bin/python
import urllib2
import sys

if len(sys.argv) == 1:
	url = raw_input("URL of site to clone: ")
else:
	url = sys.argv[1]

if "http://" not in url:
	url = "http://"+url


file = open("index.html", "w")

content = urllib2.urlopen(url).read()

file.write(content)

print file

file.close()