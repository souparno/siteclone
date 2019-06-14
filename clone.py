import requests
import sys
import socket
import os
import re

def download(resource):

	if any(s in resource for s in dataTypesToDownload):

		if " " in resource: # https://stackoverflow.com/a/4172592
			return

		while resource.startswith("/"):
			resource = resource[1:]

		if resource.startswith("https://") or resource.startswith("http://"):
			resource = resource.replace("https://", "").replace("http://", "")

		if resource.startswith("../"):
			resource = resource.replace("../", "dotdot/")

		try:
			path = resource.split("/")
			
			if len(path) != 1:
				path.pop(len(path) - 1)
				trail = "./" + base_path + "/"
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
				download = open(base_path + "/"+ resource.split("?")[len(resource.split("?")) - 2], "w")
			else:
				download = open(base_path + "/"+ resource, "w")

			print("Downloading {} to {}".format(resource, download.name))

			dContent = requests.get(url+"/"+resource).text
		
		except Exception as e:
		
			print("An error occured: " + str(e.reason))
			download.close()
			return
		
		download.write(dContent)
		download.close()
		print("Downloaded!")

socket.setdefaulttimeout(15)

dataTypesToDownload = [".jpg", ".jpeg", ".png", ".gif", ".ico", ".css", ".js", ".html"]

if len(sys.argv) == 1:
	url = input("URL of site to clone: ")
else:
	if sys.argv[1] == "-h":
		print("Usage: {} [url] [directory]".format(sys.argv[0]))
	url = sys.argv[1]

if len(sys.argv) <= 2:
    base_path = input("Directory to clone into: ")
else:
    base_path = sys.argv[2]

if "http://" not in url and "https://" not in url:
	url = "http://"+url

domain = "//".join(url.split("//")[1:])

try:
	os.mkdir(base_path)
except OSError:
	pass

with requests.Session() as r:
	try:
		content = r.get(url).text
	except Exception as e:
		print("Error: {}".format(e))

file = open(base_path + "/index.html", "w")
file.write(content)
file.close()

resources = re.split("=\"|='", content)

for resource in resources:

	resource = re.split("\"|'", resource)[0]

	download(resource)

for subdir, dirs, files in os.walk(base_path):
	for file in files:
		
		if file == ".DS_Store":
			continue
		
		f = open(os.path.join(subdir, file), 'r')
		
		content = f.read()
		if "url(" in content:
			arr = content.split("url(")
			iterations = len(arr) - 1
			i = 1
			for x in range(iterations):
				path = arr[i].split(")")[0]
				download(url+"/"+path)
				i += 1
			
print("Cloned "+url+" !")
