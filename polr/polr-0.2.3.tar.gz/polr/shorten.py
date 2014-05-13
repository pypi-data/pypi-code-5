import requests

def shorten(apikey, url, temp):
    short = requests.get('http://polr.cf/api.php', params={'apikey': apikey, 'action': 'shorten', 'url': url, "temp": temp})
    if short.ok:
        return short.text
    raise short.raise_for_status()
