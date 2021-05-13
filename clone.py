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

def getScheme():
    return urlparse(url)[0] + "://"

def getDomain():
    return getScheme() + urlparse(url)[1]

def getUrl():
    return getDomain() + urlparse(url)[2]

def getDownloadPath(item):
    schemes = [getDomain(), "http://", "https://"]
    regex = re.compile("|".join(schemes))
    item = re.sub(regex, "", item)

    return resolvePath([base_path, urlparse(item)[2]])

#  build the path by removing extra // and resolving relative path
#  ex: abc//def = abc/def
#  and abc/def/../ghi = abc/ghi
def resolvePath(path):
    temp_path = re.sub("\/\.\/|\/+", "/", "/".join(path))

    while True:
        path = temp_path
        temp_path = re.sub("(^|\/)(?!\.?\.\/)([^\/]+)\/\.\.\/*", "/", temp_path)

        if path == temp_path:
            break

    return temp_path.replace(":/", "://")


def resources(content, regex):
    items = []

    for match in re.findall(regex, content):
        items.append(''.join(match))

    return items


def replace(content, reg, fromUrl = ""):
    for resource in resources(content, reg):
        path = download(fromUrl, re.sub("\\\/", "/", resource))

        if path:
            content = content.replace(resource, resolvePath(["/", path]))

    return content


def write(dContent, download_path):
    item_path = download_path.split("/")[:-1]
    
    trail = "./"

    for folder in item_path:
        trail += folder + "/"
        try:
            os.mkdir(trail)
        except OSError:
            pass	
   
    download = open(download_path, "wb")
    for chunk in dContent:
        download.write(chunk)

    download.close()


def download(fromUrl, item):
    global downloadedFiles

    if item.startswith("."):
        item = resolvePath([fromUrl, item])

    if not urlparse(item)[1] and item.startswith("/"):
        item = resolvePath([getDomain(), item])

    if not urlparse(item)[1] and not item.startswith("/"):
        item = resolvePath([getUrl(), item])

    if not urlparse(item)[0]:
        item = resolvePath([getScheme(), item])

    download_path = getDownloadPath(item)

    if download_path in downloadedFiles:
        return download_path

    print("Downloading {} to {}".format(item, download_path))

    try:
        dContent = get(quote(item, safe=string.printable))
        write(dContent, download_path) 
        downloadedFiles[download_path] = item
        print("Downloaded!")
        return download_path

    except Exception as e:
        print("An error occured: " + str(e.reason))
        return False


downloadedFiles = {}
downloadUrls = []
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

response = get(url)
content = replace(response.read().decode('utf-8'), regex)
soup = BeautifulSoup(content, "html.parser")

for link in soup.find_all('a', href=True):
    content = content.replace(link['href'], "#")


index_html = resolvePath([getUrl(), "index.html"])
index_path = getDownloadPath(index_html)
downloadedFiles[index_path] = index_html

file = open(index_path, "w")
file.write(content)
file.close()

print(downloadedFiles)

print('Scanning for CSS based url(x) references...')
for subdir, dirs, files in os.walk(base_path):
    for file in files:
            
        if file == ".DS_Store" or file.split(".")[-1] not in textFiles:
            continue

        print("scanning  file " + os.path.join(subdir, file))

        #  d_url = os.path.join(subdir, file).replace(base_path, getDomain())
        d_url = downloadedFiles[os.path.join(subdir, file)].split(file)[0]
        f = open(os.path.join(subdir, file), 'r+')
        content = replace(f.read(), "url\s*\(['\"]*" + regex, d_url)

        f.seek(0)
        f.truncate()
        f.write(content)
        f.close()

print("Cloned " + url + " !")
