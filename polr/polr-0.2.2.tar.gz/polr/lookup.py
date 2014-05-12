import requests

def lookup(apikey, url):
    if url.startswith("http://polr.cf"):
        url = url.replace("http://polr.cf/", "")
    elif url.startswith("polr.cf"):
        url = url.replace("polr.cf/", "")
    lookup = requests.get("http://polr.cf/api.php", params= { "apikey": apikey, "action": "lookup", "url": url})
    raise lookup.raise_for_status()
    return lookup.text
