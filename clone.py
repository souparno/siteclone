import requests
import sys
import socket
import os
import re

socket.setdefaulttimeout(15)

dataTypesToDownload = [".jpg", ".jpeg", ".png", ".gif", ".ico", ".css", ".js", ".html"]

if len(sys.argv) == 1:
	url = input("URL of site to clone: ")
else:
	url = sys.argv[1]

print(sys.argv)

if len(sys.argv) <= 2:
        pathbase = input("Directory to clone into: ")
else:
        pathbase = sys.argv[2]

if "http://" not in url and "https://" not in url:
	url = "http://"+url

try:
	os.mkdir(pathbase)
except OSError:
	pass

file = open(pathbase + "/index.html", "w")


with requests.Session() as r:
	try:
		content = r.get(url).text
		print(content)
	except Error as e:
		print("Error: {}".format(e))

resources = re.split("=\"|='", content)

first = False
for resource in resources:
	if first == False:
		first = True
		continue
	resource = re.split("\"|'", resource)[0]
	if any(s in resource for s in dataTypesToDownload):
		print("Downloading " + resource)
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
			print(url+"/"+resource)
			dContent = urllib.request.urlopen(url+"/"+resource).read()
		except urllib.error.URLError as e:
			print("An error occured: " + str(e.reason))
			download.close()
			continue
		except IOError:
			pass
			continue
		download.write(dContent)
		download.close()
		print("Downloaded!")

file.write(content)

print("Cloned "+url+" !")

file.close()
