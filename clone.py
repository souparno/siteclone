import requests
import sys
import socket
import os
import re


def download(item):

	global downloadedFiles

	if any(s in item for s in dataTypesToDownload):

		if " " in item:  # https://stackoverflow.com/a/4172592
			return

		while item.startswith("/"):
			item = item[1:]

		external = False
		prefix = ""

		if "#" in item:
			item = item.split("#")[0]
		
		if item.startswith("https://"):
			external = True
			prefix = "https://"
			item = item.replace("https://", "")
			
		if item.startswith("http://"):
			external = True
			prefix = "http://"
			item = item.replace("http://", "")

		if item.startswith("../"):
			item = item.replace("../", "dotdot/")

		if item in downloadedFiles:
			return

		try:
			item_path = item.split("/")
			
			if len(item_path) != 1:
				item_path.pop(len(item_path) - 1)
				trail = "./" + base_path + "/"
				for folder in item_path:
					trail += folder+"/"
					try:
						os.mkdir(trail)
					except OSError:
						pass	

		except IOError:
			pass

		try:

			if "?" in item:
				download = open(base_path + "/" + item.split("?")[len(item.split("?")) - 2], "wb")
			else:
				download = open(base_path + "/" + item, "wb")

			print("Downloading {} to {}".format(item, download.name))

			if external:
				dContent = requests.get(prefix+item, stream=True)
			else:
				dContent = requests.get(url+"/"+item, stream=True)
		
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

# Catch root level documents in href tags
hrefs = content.split("href=\"")

for i in range( len(hrefs) - 1 ):
	href = hrefs[i+1]
	href = href.split("\"")[0]
	if "/" not in href and "." in href and ("." + href.split(".")[-1]) in dataTypesToDownload:
		download(href)

textFiles = ["css", "js", "html", "php", "json"]
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
