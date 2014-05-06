import requests
apikey = "APIKEYHERE"

class UnauthorizedError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def lookup(url):
    if url.startswith("http://polr.cf"):
        url = url.replace("http://polr.cf/", "")
    elif url.startswith("polr.cf"):
        url = url.replace("polr.cf/", "")
    lookup = requests.get("http://polr.cf/api.php", params= { "apikey": apikey, "action": "lookup", "url": url }).text
    if lookup == "<h1>404 Not Found</h1>":
        raise IndexError('No such URL found')
        return
    elif lookup == "<h1>401 Unauthorized</h1>":
        raise UnauthorizedError('Access is Unauthorized')
        return
    return lookup

def shorten(url):
    shorten = requests.get("http://polr.cf/api.php", params= { "apikey": apikey, "action": "shorten", "url": url }).text
    if shorten == "<h1>401 Unauthorized</h1>":
        raise UnauthorizedError('Access is Unauthorized')
        return
    return shorten
