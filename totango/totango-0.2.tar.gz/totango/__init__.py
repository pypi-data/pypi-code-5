import requests

class Totango:

    def __init__(self, service_id, user_id=None, user_name=None, account_id=None, account_name=None):
        self.url = 'http://sdr.totango.com/pixel.gif/'
        self.service_id = service_id
        self.account_id = account_id
        self.account_name = account_name
        self.user_id = user_id
        self.user_name = user_name

    def _get_base_payload(self, user_id=None, user_name=None, account_id=None, account_name=None, user_opts={}, account_opts={}):
        user_id = user_id or self.user_id
        if user_id is None:
            raise NameError("user_id is required")

        payload = {
            'sdr_s': self.service_id,
            'sdr_u': self.user_id,
        }

        user_name = user_name or self.user_name
        if user_name is not None:
            payload['sdr_u.name'] = user_name

        account_id = account_id or self.account_id
        if account_id is not None:
            payload['sdr_o'] = account_id

        account_name = account_name or self.account_name
        if account_name is not None:
            payload['sdr_odn'] = account_name

        for key, value in user_opts.iteritems():
            payload["sdr_u.{0}".format(key)] = value

        for key, value in account_opts.iteritems():
            payload["sdr_o.{0}".format(key)] = value

        return payload

    def _post(self, payload):
        r = requests.post(self.url, data=payload)
        r.raise_for_status()
        return r

    def track(self, module, action, user_id=None, user_name=None, account_id=None, account_name=None, user_opts={}, account_opts={}):
        user_id = user_id or self.user_id
        if user_id is None:
            raise NameError("user_id is required")

        payload = self._get_base_payload(user_id, user_name, account_id, account_name, user_opts, account_opts)
        payload['sdr_m'] = module
        payload['sdr_a'] = action

        return self._post(payload)

    def send(self, user_id=None, user_name=None, account_id=None, account_name=None, user_opts={}, account_opts={}):
        user_id = user_id or self.user_id
        if user_id is None:
            raise NameError("user_id is required")

        payload = self._get_base_payload(user_id, user_name, account_id, account_name, user_opts, account_opts)

        return self._post(payload)

