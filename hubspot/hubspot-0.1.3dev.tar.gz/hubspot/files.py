import simplejson as json
import requests
from .hsapi import HSApi, HAPIError


class Files(HSApi):

    BASE_URL = "https://api.hubapi.com/content/api/v2/files"
    FOLDERS = "https://api.hubapi.com/content/api/v2/folders"

    def upload_new_file(self, filename, folders=None, overwrite="false"):
        params = self.add_authentication({})

        data = {"overwrite": overwrite}

        if folders is not None:
            data['folders'] = folders

        files = {"files": open(filename, 'rb')}

        r = requests.post(self.BASE_URL, data=data, files=files)

        if r.status_code == 200:
            response = r.json()
            return response
        else:
            raise HAPIError(
                message="New File Post Failed",
                response=r.text,
                code=r.status_code
            )

    def get_all_metadata(self, params=None):

        allowed_params = [
            "alt_key",
            "archived",
            "created",
            "deleted_at",
            "extension",
            "folder_id",
            "id",
            "name",
            "type"
        ]

        params = {key: value for (key, value) in params if key in allowed_params}

        params['limit'] = 20

        total = self.get_total(params)

        file_metadata = []

        for page in range(1, total / 20):
            file_metadata = self.get_page(page, params)

        return file_metadata

    def get_total(self, params):

        r = requests.get(self.BASE_URL, params=params)

        if r.status_code == 200:
            response = r.json()
            return response["total_count"]
        else:
            raise HAPIError(
                message="Get Total Files failed",
                response=r.text,
                code=r.status_code
            )

    def get_page(self, page, params):

        offset = params['limit'] * page

        params = self.add_authentication({params})

        r = requests.get(self.BASE_URL, params=params)

        if r.status_code == 200:
            response = r.json()
            return response["objects"]
        else:
            raise HAPIError(
                message="Get page failed",
                response=r.text,
                code=r.status_code
            )

    def get_folder_path(self, id):

        url = self.FOLDERS + "/{id}/".format(id=id)

        r = requests.get(url)

        if r.status_code == 200:
            response = r.json()
            return response["full_path"]
        else:
            raise HAPIError(
                message="Get folder path failed",
                response=r.text,
                code=r.status_code
            )