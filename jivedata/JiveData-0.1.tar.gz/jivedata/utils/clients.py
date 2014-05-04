import requests


class Client(object):
    def __init__(self, client_id, client_secret,
                 api_base='https://api.jivedata.com',
                 grant_type='client_credentials'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_base = api_base
        self.grant_type = grant_type

    def get_token(self):
        params = {'grant_type': self.grant_type,
                  'client_id': self.client_id,
                  'client_secret': self.client_secret}
        response = requests.get(self.api_base + '/oauth/token/',
                                params=params, verify=False,
                                timeout=60)

        try:
            self.token = response.json()
        except:
            raise Exception(response.text)

        if 'error' in self.token:
            if self.token['error'] == 'invalid_client':
                raise Exception('Your client credentials are invalid')
            else:
                raise Exception(self.token)

        if 'access_token' not in self.token:
            raise Exception(self.token)

    def get_protected(self, endpoint, params={}):
        self.get_token()
        params['pretty'] = 'true'
        headers = {'Authorization': 'Bearer %s' % self.token['access_token']}
        r = requests.get(self.api_base + endpoint, params=params,
                         headers=headers, verify=False, timeout=60)
        self.text = r.text
        try:
            self.results = r.json()
        except:
            raise Exception(self.text)
