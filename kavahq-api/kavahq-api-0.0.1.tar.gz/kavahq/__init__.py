# -*- coding: utf-8 -*-
__version__= '0.0.1'
import urllib
import urllib2
import base64
import json


API_SETTINGS = {
    'kava_url': 'https://kavahq.com/api/',
    'username': '',
    'password': '',
}


class Company(object):

    def __init__(self, company_slug, kava_api):
        self.company_slug = company_slug
        self.api = kava_api

    def projects(self):
        return self.api.get_projects(company=self.company_slug)

    def project(self, slug):
        return self.api.get_project(slug, company=self.company_slug)

    def add_project(self, data):
        """
        Doesn't work because ProjectAddResource needs company name instead slug.
        """
        data.update({'company': self.company_slug})
        return self.api._make_request('project/add/', data)


class KavaApi(object):

    class ApiError(Exception):
        pass

    class UnauthorizedError(ApiError):
        pass

    def __init__(self, *args, **kwargs):
        self.settings = dict(API_SETTINGS)
        self.settings.update(kwargs)

    def get_company(self, slug):
        return Company(company_slug=slug, kava_api=self)

    def get_projects(self, **kwargs):
        filters = kwargs
        return self._make_request('project/', filters, force_get=True)['projects']

    def get_project(self, project_slug, company=None):
        filters = {}
        if company:
            filters['company'] = company

        return self._make_request('project/%s/' % project_slug, filters,
                                  force_get=True)

    def _make_request(self, resource_uri, post_data=None, force_get=False):
        """
        This method is used to make GET and POST requests to API
        with BaseAuth and handling api errors.

        Params:
        post_data - dict to send in POST or GET
        force_get - if True, than post_data will be sended in query-string

        Returns:
        If request was success - returns data under 'message' key in response.
        """

        post_data_str = None
        if post_data:
            post_data_str = urllib.urlencode(post_data)

        request_url = '%s%s' % (
            self.settings['kava_url'], resource_uri)

        if post_data_str and force_get:
            request = urllib2.Request(request_url + '?%s' % post_data_str)
        else:
            request = urllib2.Request(request_url, data=post_data_str)

        user_pass_string = '%s:%s' % (self.settings['username'],
                                      self.settings['password'])

        base64string = base64.standard_b64encode(user_pass_string)
        request.add_header("Authorization", "Basic %s" % base64string)

        try:
            print request_url
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            if e.code == 401:
                raise self.UnauthorizedError(e.read())
            elif e.code == 400:
                content = e.read()
                error_msg = content
                try:
                    resp_message = json.loads(content)['message']
                except:
                    pass
                else:
                    if 'errors' in resp_message:
                        error_msg = resp_message['errors']

                raise self.ApiError(error_msg)
            else:
                raise

        resp_data = response.read()
        response.close()

        api_resp = json.loads(resp_data)
        result_data = api_resp['message']
        result_code = api_resp['code']

        # Return data
        return result_data
