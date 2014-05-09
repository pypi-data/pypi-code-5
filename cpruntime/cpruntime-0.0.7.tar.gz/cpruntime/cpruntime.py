import os
import httplib2
import json
def get_hosts_info_by_service_type(service_type):
    fullUrl=os.environ['endpoint']+"/meta-data/service/"+os.environ['app_uuid']
    resp,content =httplib2.Http().request(fullUrl)
    contentjsondic = json.loads(content)
    [{key:value} for key, value in contentjsondic.iteritems() if key.startswith(service_type)]

