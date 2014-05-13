from urllib.parse import quote

catalogs = [
]

def download(get, catalog):
    raise NotImplementedError

def apikey(get, catalog, datetime):
    url = '%s/developer_manager/action_insert?_=%s' % (catalog, datetime.strftime('%s%f')[:-3])
    response = get(url)
    data = json.loads(response.text)
    return data['pApiKey']

def search(get, catalog, terms, apikey, page):
    args = (catalog.replace('opendata.junar.com', 'cloudapi.junar.com'), quote(terms), apikey)
    url = '%s/datastreams/search?query=%s&auth_key=%s' % args
    print(url)
    1/0
    response = get(url)
    print(response.text)
    1/0
