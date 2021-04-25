import sys
import os
import ssl
import re
import socks
import socket
from urllib.request import Request, urlopen


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

def resources(content):
    items = []
    regex = "a-zA-Z0-9\.\/:-"
    regex = "([" + regex + "]+)" + str("(" + "|".join(dataTypesToDownload) + ")").replace(".", "\.") + "([" + regex + "?=&]*)"

    for match in re.findall(regex, content):
       items.append(''.join(match))

    return items

def download(item):

    global downloaded
    global downloadPaths
    global downloadedFiles
    global domain
    global url

    #  if any(s in item for s in dataTypesToDownload):

    if " " in item:  # https://stackoverflow.com/a/4172592
        return

    while item.startswith("/"):
        item = item[1:]

    external = False
    prefix = ""

    if "#" in item:
        item = item.split("#")[0]

    if item.startswith(url):
        external = True
        prefix = url
        item = item.replace(url, "")

    if item.startswith(domain):
        external = True
        prefix = domain
        item = item.replace(domain, "")

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
            download_path = build_path("/" + item.split("?")[len(item.split("?")) - 2])
        else:
            download_path = build_path("/" + item)

        #  If the element is already downloaded make downloaded flag true  and move to the 
        #  end of the list so that the content can be overwritten with the correct path
        #  if download_path in downloadPaths:
        #      print("======= H E Y   C H E C K   T H I S   O U T =====")
        #      downloaded = True
        #      downloadPaths.pop(downloadPaths.index(download_path))
        #      return

        download = open(build_path(base_path + download_path), "wb")
        downloadPaths.append(download_path)
 
        if external:
            d_url = build_path(prefix + item)
        else:
            d_url = build_path(url + "/" + item)

        #  adding the / to http:/ or https:/ that got removed while build_path
        #  for protocol in re.findall("http:\/|https:\/",  d_url):
        #      d_url = re.sub("http:\/|https:\/", protocol + "/", d_url)       
        d_url = re.match("(http:\/|https:\/)(.+)", d_url)
        d_url = d_url.group(1) + "/" + d_url.group(2)

        print("Downloading {} to {}".format(d_url, download.name))
        dContent = get(d_url)
    except Exception as e:

        print("An error occured: " + str(e.reason))
        download.close()
        return
    
    for chunk in dContent:
        download.write(chunk)

    download.close()
    #  downloadedFiles.append(resource)
    downloaded = True
    print("Downloaded!")


downloadedFiles = []
downloadPaths = []
downloaded = False
dataTypesToDownload = [".svg", ".jpg", ".jpeg", ".png", ".gif", ".ico", ".css", ".js", ".html", ".php", ".json", ".ttf", ".otf", ".woff", ".woff2", ".eot", ".mp4"]
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

domain = "//".join(url.split("//")[1:])

try:
    os.mkdir(base_path)
except OSError:
    pass


response = get(url)
content = response.read().decode('utf-8')

for resource in resources(content):
    download(resource) 

    if downloaded == True:
        content = content.replace(resource, downloadPaths[-1])
        downloaded = False

        #  print("==========================")
        #  print("replacing " + resource + " with " + downloadPaths[-1])
        #  print("==========================")



file = open(build_path(base_path + "/index.html"), "w")
file.write(content)
file.close()

    #  if resource == "/wp-content/themes/twentysixteen/images/newdesign/appfutura.svg":
    #      break


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
            


        for resource in arr:
            if "." + resource.split(".")[-1] in dataTypesToDownload:
                download(resource)

                
                if downloaded == True:
                    print("modifying the resource links") 
                    arr[arr.index(resource)] = downloadPaths[-1] 
                    downloaded = False


        f.seek(0)
        f.truncate()
        f.write("".join(arr))
        f.close()


#  def get_listing(path):
#      file_listing = []

#      for subdir, dirs, files in os.walk(path):
#          for f in files:
#              file_listing.append(os.path.join(subdir, f))

#      return file_listing

#  before = []
#  after = get_listing(base_path)
#  diff = [f for f in after if not f in before]

#  while diff:
    
#      for file in diff:

#          if file.split(".")[-1]  == "DS_Store" or file.split(".")[-1] not in textFiles:
#              continue

#          f = open(file, 'r+')

#          print("S C A N N I N G   F I L E : " + f.name)
      

#          content = f.read()

#          for resource in resources(content):
#              download(resource) 
        
#              if downloaded == True:
#                  content = content.replace(resource, downloadPaths[-1])
#                  downloaded = False
            

#          f.seek(0)
#          f.truncate()
#          f.write(content)
#          f.close()

#      before = after
#      after = get_listing(base_path)
#      diff = [f for f in after if not f in before]


print("Cloned " + url + " !")
