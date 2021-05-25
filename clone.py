import sys
import os
import ssl
import re
import socks
import socket
import string
from urllib.request import Request, urlopen
from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup

def get(url):
    IP_ADDR = '127.0.0.1'
    PORT = 9050

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    request = Request(url)
    socks.set_default_proxy(socks.SOCKS5, IP_ADDR, PORT)
    socket.socket = socks.socksocket

    return  urlopen(request, context=ctx)

def getScheme(url):
    return urlparse(url)[0] + "://"

def getDomain(url):
    return getScheme(url) + urlparse(url)[1]

def getUrl(url):
    return getDomain(url) + urlparse(url)[2]

def getItem(url, item):
    item = resolvePath([re.sub("^\/{2,}", getScheme(url), item)])

    item = resolvePath([re.sub("^\/{1,1}", getDomain(url) + "/", item)])

    if not item.startswith("http") or item.startswith("."):
        item = resolvePath([getUrl(url), item])

    return item

def getDownloadPath(item):
    item = item.replace(getScheme(url), "")

    return resolvePath([base_path, urlparse(item)[2]])

def groupUrl(path):
    return re.match("^(https:\/\/|http:\/\/|[\/]+)*(.*)", path)

def cleanPath(path):
    return re.sub("\/\.\/|\/+|\\\/", "/", path)

def resolvePath(path):
    path = groupUrl("/".join(path))
    temp_path = cleanPath(path.group(2))

    while True:
        _path = temp_path
        temp_path = re.sub("(^|\/)(?!\.?\.\/)([^\/]+)\/\.\.\/*", "/", temp_path)

        if _path == temp_path:
            break

    return (path.group(1) or '')  + temp_path

def resources(content, regex):
    items = []

    for match in re.findall(regex, content):
        items.append(''.join(match))

    return items

def replace(content, reg, fromUrl, overwrite=True):
    for resource in resources(content, reg):
        path = download(fromUrl, resource)

        if path and overwrite:
            path = "/" + path.replace(resolvePath([base_path, "/"]), "")
            content = content.replace(resource, path)

    return content

def write(content, path):
    item_path = path.split("/")[:-1]

    trail = "./"

    for folder in item_path:
        trail += folder + "/"
        try:
            os.mkdir(trail)
        except OSError:
            pass	
   
    download = open(path, "wb")
    for chunk in content:
        download.write(chunk)

    download.close()

def download(url, item):
    global downloadedFiles

    item = getItem(url, item)

    path = getDownloadPath(item)

    if path in downloadedFiles:
        return False

    print("Downloading {} to {}".format(item, path))

    try:
        content = get(item)
        write(content, path)
        downloadedFiles[path] = item
        print("Downloaded!")
        return path

    except Exception as e:
        print("An error occured: " + str(e.reason))
        return False

def downloadFromtextFiles():
    for subdir, dirs, files in os.walk(base_path):
        for file in files:
     
            if file == ".DS_Store" or file.split(".")[-1] not in textFiles:
                continue

            print("scanning  file " + os.path.join(subdir, file))

            url = downloadedFiles[os.path.join(subdir, file)].split(file)[0]

            f = open(os.path.join(subdir, file), 'r+')

            content = f.read()
            content = replace(content, "url\s*\(['\"]*" + regex, url)
            content = replace(content, "sourceMappingURL=" + regex, url, overwrite=False)

            f.seek(0)
            f.truncate()
            f.write(content)
            f.close()

downloadedFiles = {}
dataTypesToDownload = [".svg", ".jpg", ".jpeg", ".png", ".gif", ".ico", ".css", ".js", ".html", ".php", ".json", ".ttf", ".otf", ".woff2", ".woff", ".eot", ".mp4"]
textFiles = ["css", "js", "html", "php", "json"]

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
    url = "http://" + url

regex = "([^=\"'(\s]+)" + str("(" + "|".join(dataTypesToDownload) + ")").replace(".", "\.") + "([^\"')>\s]*)"

item = resolvePath([getUrl(url), "index.html"])
path = getDownloadPath(item)
downloadedFiles[path] = item
write(get(url), path)

content = replace(get(url).read().decode('utf-8'), regex, getUrl(url))

#  soup = BeautifulSoup(content, "html.parser")
#  for link in soup.find_all('a', href=True):
#      content = content.replace(link['href'], "#")

downloadFromtextFiles()

f = open(path, 'r+')
f.seek(0)
f.truncate()
f.write(content)
f.close()

print("Cloned " + url + " !")
