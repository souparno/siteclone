import sys
import os
import re
import string
import requests
from urllib.parse import quote, urlparse

def get_tor_session():
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    return session

def get(url):
    url = quote(url, safe=string.printable)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    return session.get(url, headers=headers)

def getScheme(url):
    return urlparse(url)[0] + "://"

def getDomain(url):
    return getScheme(url) + urlparse(url)[1]

def getUrl(url):
    return getDomain(url) + "/" + urlparse(url)[2].strip("/\\")

def getItem(url, item):
    item = resolvePath([re.sub("^\/{2,}", getScheme(url), item)])

    item = resolvePath([re.sub("^\/{1,1}", getDomain(url) + "/", item)])

    if not item.startswith("http") or item.startswith("."):
        item = resolvePath([getUrl(url), item])

    return item

def getDownloadPath(item):
    item = item.replace(getScheme(url), "")

    return resolvePath([base_path, urlparse(item)[2]])

def splitUrl(path):
    return re.match("^(https:\/\/|http:\/\/|[\/]+)*(.*)", path)

def cleanPath(path):
    return re.sub("\/\.\/|\/+|\\\/", "/", path)

def resolvePath(path):
    path = splitUrl("/".join(path))
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
            path = "/" + "/".join(path.split("/")[1:])
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

def validate_url(url):
    # List of file extensions to be removed 
    parsed_url = urlparse(url)
    
    # Remove file extensions from the path
    path_without_extensions = parsed_url.path
    for extension in dataTypesToDownload:
        # Use regular expression to remove extension only if it is at the end of the path
        path_without_extensions = re.sub(re.escape(extension) + r'$', '', path_without_extensions)
    
    # Check for invalid characters in the path
    invalid_chars = set(string.punctuation.replace('/', '').replace('-', '').replace('.', '').replace('_', '').replace('@', ''))
    if any(char in invalid_chars for char in path_without_extensions):
        return False
    
    return True

def download(url, item):
    global downloadedFiles

    item = getItem(url, item)

    if not validate_url(item):
        print("INVALID URL -------> ", item)
        return False

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

session = get_tor_session()
downloadedFiles = {}
dataTypesToDownload = [".svg", ".jpg", ".jpeg", ".png", ".gif", ".ico", ".css", ".js", ".html", ".php", ".json", ".ttf", ".otf", ".woff2", ".woff", ".eot", ".mp4", ".ogg"]
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

_file_name = getUrl(url).split("/")[-1] if getUrl(url).endswith(".html") else "index.html"
_url = getUrl(url).split(_file_name)[0]

item = resolvePath([_url, _file_name])
path = getDownloadPath(item)
downloadedFiles[path] = item
write(get(url), path)

content = replace(get(url).text, regex, _url)

downloadFromtextFiles()

f = open(path, 'r+')
f.seek(0)
f.truncate()
f.write(content)
f.close()

print("Cloned " + url + " !")
