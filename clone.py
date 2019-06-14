import requests
import sys
import socket
import os
import re

def download(resource):

	global downloadedFiles

	if any(s in resource for s in dataTypesToDownload):

		if " " in resource: # https://stackoverflow.com/a/4172592
			return

		while resource.startswith("/"):
			resource = resource[1:]

		external = False
		prefix = ""
		
		if resource.startswith("https://"):
			external = True
			prefix="https://"
			resource = resource.replace("https://", "")
			
		if resource.startswith("http://"):
			external = True
			prefix="http://"
			resource = resource.replace("http://", "")

		if resource.startswith("../"):
			resource = resource.replace("../", "dotdot/")

		if resource in downloadedFiles:
			return

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
				download = open(base_path + "/"+ resource.split("?")[len(resource.split("?")) - 2], "wb")
			else:
				download = open(base_path + "/"+ resource, "wb")

			print("Downloading {} to {}".format(resource, download.name))

			if external:
				dContent = requests.get(prefix+resource, stream=True)
			else:
				dContent = requests.get(url+"/"+resource, stream=True)
		
		except Exception as e:
		
			print("An error occured: " + str(e.reason))
			download.close()
			return
		
		for chunk in dContent:
			download.write(chunk)

		download.close()
		print("Downloaded!")
		downloadedFiles.append(resource)

socket.setdefaulttimeout(15)

downloadedFiles = []
dataTypesToDownload = [".jpg", ".jpeg", ".png", ".gif", ".ico", ".css", ".js", ".html", ".php", ".json"]

if len(sys.argv) == 1:
	url = input("URL of site to clone: ")
else:
	if sys.argv[1] == "-h":
		print("Usage: {} [url] [directory]".format(sys.argv[0]))
		exit()
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

#Catch root level documents in href tags
hrefs = content.split("href=\"")

for i in range( len(hrefs) - 1 ):
	href = hrefs[i+1]
	href = href.split("\"")[0]
	if "/" not in href and "." in href and ("." + href.split(".")[-1]) in dataTypesToDownload:
		download(href)

textFiles = [ "css", "js", "html", "php", "json"]
print('Scanning for CSS based url(x) references...')

for subdir, dirs, files in os.walk(base_path):
	for file in files:
		
		if file == ".DS_Store" or file.split(".")[-1] not in textFiles:
			continue

		f = open(os.path.join(subdir, file), 'r')
		
		content = f.read()
		if "url(" in content:
			arr = content.split("url(")
			iterations = len(arr) - 1
			i = 1
			for x in range(iterations):
				path = arr[i].split(")")[0]
				download(path)
				i += 1
			
print("Cloned "+url+" !")
