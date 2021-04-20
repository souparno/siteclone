import sys
import os
import ssl
import re
import socks
import socket
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


#  build the path by removing extra // and resolving relative path
#  ex: abc//def = abc/def
#  and abc/def/../ghi = abc/ghi
def build_path(path):
    temp_path = re.sub("\/\.\/|\/+", "/", path)
    
    while True:
        path = temp_path
        temp_path = re.sub("(^|\/)(?!\.?\.\/)([^\/]+)\/\.\.\/*", "/", temp_path)

        if path == temp_path:
            break

    return temp_path

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

def download(item):

    global downloaded
    global downloadPaths
    global downloadedFiles
    global url

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

            download_path = ""

            if "?" in item:
                download_path = build_path("/" + item.split("?")[len(item.split("?")) - 2])
            else:
                download_path = build_path("/" + item)

            download = open(build_path(base_path + download_path), "wb")
            downloadPaths.append(download_path)
           
            print("Downloading {} to {}".format(item, download.name))
            
            if external:
                dContent = get(prefix+item)
            else:
                dContent = get(url+"/"+item)
        
        except Exception as e:
 
            print("An error occured: " + str(e.reason))
            download.close()
            return
        
        for chunk in dContent:
            download.write(chunk)

        download.close()
        print("Downloaded!")
        downloadedFiles.append(resource)
        downloaded = True



downloadedFiles = []
downloadPaths = []
downloaded = False
dataTypesToDownload = [".svg", ".jpg", ".jpeg", ".png", ".gif", ".ico", ".css", ".js", ".html", ".php", ".json", ".ttf", ".otf", ".woff", ".woff2", ".eot"]

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


response = get(url)
content = response.read().decode('utf-8')
soup = BeautifulSoup(content, "html.parser")


#  Downloading all the css ref in the link tag
for link in soup.find_all('link', href=True):
    resource = link['href']
    download(resource)

    if downloaded == True:
        print("link href attribute modified !")

        link['href'] = downloadPaths[-1]
        downloaded = False


#  Downloading all the js in the script src attribute
for script in soup.find_all('script', src=True):
    resource = script['src']
    download(resource)

    if downloaded == True:
        print("script src attribute modified !")

        script['src'] = downloadPaths[-1]
        downloaded = False


#  Download all the image src links to local
for img in soup.find_all('img', src=True):
    resource = img['src']
    download(resource)

    if downloaded == True:
        print("img src attribute modified !")

        img['src'] = downloadPaths[-1]
        downloaded = False

file = open(build_path(base_path + "/index.html"), "w")
file.write(str(soup))
file.close()

#  resources = re.split("=\"|='", content)

#  for resource in resources:

#          resource = re.split("\"|'", resource)[0]

#          download(resource)
    
#  # Catch root level documents in href tags
#  hrefs = content.split("href=\"")

#  for i in range( len(hrefs) - 1 ):
#          href = hrefs[i+1]
#          href = href.split("\"")[0]
#          if "/" not in href and "." in href and ("." + href.split(".")[-1]) in dataTypesToDownload:
#                  download(href)


textFiles = ["css", "js", "html", "php", "json"]
print('Scanning for CSS based url(x) references...')

for subdir, dirs, files in os.walk(base_path):
    for file in files:
            
        if file == ".DS_Store" or file.split(".")[-1] not in textFiles:
            continue

        f = open(os.path.join(subdir, file), 'r+')
        
        print("Scanning  File " + f.name)

        arr = []
        content = f.read()

        for item in re.split("(url\(.*?\))", content):
            for i in re.split("(url\()(.*?)(\))", item):
                arr.append(i) 
            


        for elm in arr:
            if "." + elm.split(".")[-1] in dataTypesToDownload:
                resource = elm
                download(resource)

                
                if downloaded == True:
                    print("modifying the resource links") 
                    arr[arr.index(elm)] = downloadPaths[-1] 
                    downloaded = False


        f.seek(0)
        f.truncate()
        f.write("".join(arr))
        f.close()


print("Cloned "+url+" !")
