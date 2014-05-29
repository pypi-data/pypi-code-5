__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

import hashlib
from urllib import request
import time

from pymal.consts import HOST_NAME, MALAPI_NONE_TIME, MALAPPINFO_FORMAT_TIME,\
    MALAPPINFO_NONE_TIME, MALAPI_FORMAT_TIME
from pymal.decorators import my_load, SingletonFactory
from pymal.Manga import Manga
from pymal.global_functions import get_content_wrapper_div

__all__ = ['MyManga']


class MyManga(object, metaclass=SingletonFactory):
    """
    Saves an account data about manga.
    
    Attributes:
        my_enable_discussion - boolean
        my_id - int
        my_status - int.  #TODO: put the dictanary here.
        my_score - int.
        my_start_date - string as mmddyyyy.
        my_end_date - string as mmddyyyy.
        my_priority - int.
        my_storage_type - int.  #TODO: put the dictnary here.
        my_is_rereading - boolean.
        my_completed_chapters - int.
        my_completed_volumes - int.
        my_downloaded_chapters - int.
        my_times_reread - int.
        my_reread_value - int.
        my_tags - string.
        my_comments - string
        my_fan_sub_groups - string.
    """
    __all__ = ['my_enable_discussion', 'my_id', 'my_status', 'my_score',
               'my_start_date', 'my_end_date', 'my_priority',
               'my_storage_type', 'my_is_rereading',
               'my_completed_chapters', 'my_completed_volumes',
               'my_downloaded_chapters', 'my_times_reread', 'my_reread_value',
               'my_tags', 'my_comments', 'my_fan_sub_groups', 'my_reload',
               'update', 'delete']

    __MY_LOGIN_URL = request.urljoin(HOST_NAME, 'login.php')
    __TAG_SEPARATOR = ';'
    __MY_MAL_URL = request.urljoin(
        HOST_NAME, 'panel.php?go=editmanga&id={0:d}')
    __MY_MAL_DELETE_URL = request.urljoin(
        HOST_NAME, 'api/mangalist/delete/{0:d}.xml')
    __MY_MAL_UPDATE_URL = request.urljoin(
        HOST_NAME, 'api/mangalist/update/{0:d}.xml')
    __DATA_FORM = 'username={0:s}&password={1:s}&cookie=1&sublogin=Login'

    def __init__(self, mal_id: int or Manga, my_mal_id, account,
                 my_mal_xml: None=None):
        """
        """
        if isinstance(mal_id, Manga):
            self.obj = mal_id
        else:
            self.obj = Manga(mal_id, mal_xml=my_mal_xml)

        self.__my_mal_url = self.__MY_MAL_URL.format(my_mal_id)

        self._is_my_loaded = False
        self._account = account
        self.__data_form = self.__DATA_FORM.format(
            self._account._username, self._account._password).encode('utf-8')

        self.__my_mal_id = my_mal_id
        self.__my_status = None
        self.my_enable_discussion = False
        self.__my_score = None
        self.__my_start_date = None
        self.__my_end_date = None
        self.__my_priority = 0
        self.__my_storage_type = 0
        self.__my_comments = ''
        self.__my_fan_sub_groups = ''
        self.__my_tags = None
        self.__my_retail_volumes = 0

        self.__my_is_rereading = None
        self.__my_completed_chapters = None
        self.__my_completed_volumes = None
        self.__my_downloaded_chapters = 0
        self.__my_times_reread = 0
        self.__my_reread_value = None

        if my_mal_xml is not None:
            self.__my_id = int(my_mal_xml.find('my_id').text.strip())
            self.__my_status = int(my_mal_xml.find('my_status').text.strip())
            if my_mal_xml.find('my_rereadingg').text is not None:
                self.__my_is_rereading = bool(
                    int(my_mal_xml.find('my_rereadingg').text.strip()))
            else:
                self.__my_is_rereading = False
            self.__my_completed_episodes = int(
                my_mal_xml.find('my_read_chapters').text.strip())
            self.__my_completed_volumes = int(
                my_mal_xml.find('my_read_volumes').text.strip())
            self.__my_score = int(my_mal_xml.find('my_score').text.strip())
            my_start_date = my_mal_xml.find('my_start_date').text.strip()
            if my_start_date == MALAPPINFO_NONE_TIME:
                self.__my_start_date = MALAPI_NONE_TIME
            else:
                my_start_date = time.strptime(
                    my_start_date, MALAPPINFO_FORMAT_TIME)
                self.__my_start_date = time.strftime(
                    MALAPI_FORMAT_TIME, my_start_date)
            my_end_date = my_mal_xml.find('my_finish_date').text.strip()
            if my_end_date == MALAPPINFO_NONE_TIME:
                self.__my_end_date = MALAPI_NONE_TIME
            else:
                my_end_date = time.strptime(
                    my_end_date, MALAPPINFO_FORMAT_TIME)
                self.__my_end_date = time.strftime(
                    MALAPI_FORMAT_TIME, my_end_date)
            self.__my_reread_value = int(
                my_mal_xml.find('my_rereading_chap').text.strip())
            my_tags_xml = my_mal_xml.find('my_tags')
            if my_tags_xml.text is None:
                self.__my_tags = ''
            else:
                self.__my_tags = my_tags_xml.text.strip().split(
                    self.__TAG_SEPARATOR)

    @property
    def my_id(self):
        return self.__my_mal_id

    @property
    def my_status(self):
        if self.__my_status is None:
            self.my_reload()
        return self.__my_status

    @property
    def my_score(self):
        if self.__my_score is None:
            self.my_reload()
        return self.__my_score

    @property
    def my_start_date(self):
        if self.__my_start_date is None:
            self.my_reload()
        return self.__my_start_date

    @property
    def my_end_date(self):
        if self.__my_end_date is None:
            self.my_reload()
        return self.__my_end_date

    @property
    @my_load
    def my_priority(self):
        return self.__my_priority

    @property
    @my_load
    def my_storage_type(self):
        return self.__my_storage_type

    @property
    @my_load
    def my_storage_value(self):
        return self.__my_storage_value

    @property
    def my_is_rereading(self):
        if self.__my_is_rereading is None:
            self.my_reload()
        return self.__my_is_rereading

    @property
    def my_completed_chapters(self):
        if self.__my_completed_chapters is None:
            self.my_reload()
        return self.__my_completed_chapters

    @property
    def my_completed_volumes(self):
        if self.__my_completed_volumes is None:
            self.my_reload()
        return self.__my_completed_volumes

    @property
    @my_load
    def my_downloaded_chapters(self):
        return self.__my_downloaded_chapters

    @property
    def my_times_reread(self):
        if self.__my_times_reread is None:
            self.my_reload()
        return self.__my_times_reread

    @property
    def my_reread_value(self):
        if self.__my_reread_value is None:
            self.my_reload()
        return self.__my_reread_value

    @property
    def my_tags(self):
        if self.__my_tags is None:
            self.my_reload()
        return self.__my_tags

    @property
    @my_load
    def my_comments(self):
        return self.__my_comments

    @property
    @my_load
    def my_fan_sub_groups(self):
        return self.__my_fan_sub_groups

    @property
    @my_load
    def my_retail_volumes(self):
        return self.__my_retail_volumes

    def my_reload(self):
        # Getting content wrapper <div>
        content_wrapper_div = get_content_wrapper_div(
            self.__my_mal_url, self._account.auth_connect)

        bas_result = content_wrapper_div.find(name='div',
                                              attrs={'class': 'badresult'})
        if bas_result is not None:
            self._account.connect(self.__MY_LOGIN_URL, data=self.__data_form)

            # Getting content wrapper <div>
            content_wrapper_div = get_content_wrapper_div(
                self.__my_mal_url, self._account.auth_connect)

        # Getting content <td>
        content_div = content_wrapper_div.find(
            name="div", attrs={"id": "content"}, recursive=False)
        assert content_div is not None

        content_td = content_div.table.tr.td
        assert content_td is not None

        # Getting content rows <tr>
        content_form = content_td.find(name="form", attrs={'id': "mangaForm"})
        assert 'mangaForm' == content_form['id'], content_form['id']
        content_rows = content_form.table.tbody.findAll(
            name="tr", recursive=False)

        contents_divs_index = 2

        # Getting my_status
        status_select = content_rows[contents_divs_index].find(
            name="select", attrs={"id": "status", "name": "status"})
        assert status_select is not None
        # TODO: make this look better
        status_selected_options = [
            x
            for x in status_select.findAll(name="option")
            if 'selected' in x.attrs
        ]
        assert 1 == len(status_selected_options)
        self.__my_status = int(status_selected_options[0]['value'])

        is_reread_node = content_rows[contents_divs_index].find(
            name="input", attrs={"id": "rereadingBox"})
        assert is_reread_node is not None
        self.__my_is_rereading = bool(is_reread_node['value'])
        contents_divs_index += 1

        # Getting read volumes
        read_input = content_rows[contents_divs_index].\
            find(name="input", attrs={"id": "vol_read",
                                      "name": "vol_read"})
        assert read_input is not None
        self.__my_completed_volumes = int(read_input['value'])
        contents_divs_index += 1

        # Getting read chapters
        read_input = content_rows[contents_divs_index].\
            find(name="input", attrs={"id": "chap_read",
                                      "name": "chap_read"})
        assert read_input is not None
        self.__my_completed_chapters = int(read_input['value'])
        contents_divs_index += 1

        # Getting my_score
        score_select = content_rows[contents_divs_index].find(
            name="select", attrs={"name": "score"})
        assert score_select is not None
        score_selected_option = score_select.find(
            name="option", attrs={"selected": ""})
        assert score_selected_option is not None
        self.__my_score = int(float(score_selected_option['value']))
        contents_divs_index += 1

        # Getting my_tags...
        tag_content = content_rows[contents_divs_index]
        tag_textarea = tag_content.find(
            name="textarea", attrs={"name": "tags"})
        self.__my_tags = tag_textarea.text
        contents_divs_index += 1

        # Getting start date
        start_month_date_node = content_rows[contents_divs_index].find(
            name="select", attrs={"name": "startMonth"})
        assert start_month_date_node is not None
        start_month_date = start_month_date_node.find(
            name="option", attrs={"selected": ""})

        start_day_date_node = content_rows[contents_divs_index].find(
            name="select", attrs={"name": "startDay"})
        assert start_day_date_node is not None
        start_day_date = start_day_date_node.find(
            name="option", attrs={"selected": ""})

        start_year_date_node = content_rows[contents_divs_index].find(
            name="select", attrs={"name": "startYear"})
        assert start_year_date_node is not None
        start_year_date = start_year_date_node.find(
            name="option", attrs={"selected": ""})

        start_month_date = str(start_month_date['value']).zfill(2)
        start_day_date = str(start_day_date['value']).zfill(2)
        start_year_date = str(start_year_date['value']).zfill(2)
        self.__my_start_date = start_month_date + \
            start_day_date + start_year_date
        contents_divs_index += 1

        # Getting end date
        end_month_date_node = content_rows[contents_divs_index].find(
            name="select", attrs={"name": "endMonth"})
        assert end_month_date_node is not None
        end_month_date = end_month_date_node.find(
            name="option", attrs={"selected": ""})

        end_day_date_node = content_rows[contents_divs_index].find(
            name="select", attrs={"name": "endDay"})
        assert end_day_date_node is not None
        end_day_date = end_day_date_node.find(
            name="option", attrs={"selected": ""})

        end_year_date_node = content_rows[contents_divs_index].find(
            name="select", attrs={"name": "endYear"})
        assert end_year_date_node is not None
        end_year_date = end_year_date_node.find(
            name="option", attrs={"selected": ""})

        end_month_date = str(end_month_date['value']).zfill(2)
        end_day_date = str(end_day_date['value']).zfill(2)
        end_year_date = str(end_year_date['value']).zfill(2)
        self.__my_end_date = end_month_date + end_day_date + end_year_date
        contents_divs_index += 1

        # Getting priority
        priority_node = content_rows[contents_divs_index].find(
            name="select", attrs={"name": "priority"})
        assert priority_node is not None
        selected_priority_node = priority_node.find(
            name="option", attrs={"selected": ""})
        assert selected_priority_node is not None
        self.__my_priority = int(selected_priority_node['value'])
        contents_divs_index += 1

        # Getting storage
        storage_type_node = content_rows[contents_divs_index].find(
            name="select", attrs={"id": "storageSel"})
        assert storage_type_node is not None
        selected_storage_type_node = storage_type_node.find(
            name="option", attrs={"selected": ""})
        if selected_storage_type_node is None:
            self.__my_storage_type = 0
        else:
            self.__my_storage_type = int(selected_storage_type_node['value'])
        contents_divs_index += 1

        # Getting downloaded episodes
        downloaded_chapters_node = content_rows[contents_divs_index].\
            find(name="input", attrs={'id': "dChap",
                                      'name': 'downloaded_chapters'})
        assert downloaded_chapters_node is not None
        self.__my_downloaded_chapters == int(downloaded_chapters_node['value'])
        contents_divs_index += 1

        # Getting time reread
        times_reread_node = content_rows[contents_divs_index].find(
            name="input", attrs={'name': 'times_read'})
        self.__my_times_reread == int(times_reread_node['value'])
        assert times_reread_node is not None
        contents_divs_index += 1

        # Getting reread value
        reread_value_node = content_rows[contents_divs_index].find(
            name="select", attrs={'name': 'reread_value'})
        assert reread_value_node is not None
        reread_value_option = reread_value_node.find(
            name='option', attrs={'selected': ''})
        if reread_value_option is None:
            self.__my_reread_value = 0
        else:
            self.__my_reread_value = int(reread_value_option['value'])
        contents_divs_index += 1

        # Getting comments
        comment_content = content_rows[contents_divs_index]
        comment_textarea = comment_content.find(
            name="textarea", attrs={"name": "comments"})
        self.__my_comments = comment_textarea.text
        contents_divs_index += 1

        # Getting discuss flag
        discuss_node = content_rows[contents_divs_index].find(
            name='input', attrs={"name": "discuss"})
        assert discuss_node is not None
        self._is_my_loaded = True

    def to_xml(self):
        data = self.MY_MAL_XML_TEMPLATE.format(
            self.my_completed_chapters,
            self.my_completed_volumes,
            self.my_status,
            self.my_score,
            self.my_downloaded_chapters,
            self.my_times_reread,
            self.my_reread_value,
            self.my_start_date,
            self.my_end_date,
            self.my_priority,
            self.my_is_rereading,
            self.my_enable_discussion,
            self.my_comments,
            self.my_fan_sub_groups,
            self.my_tags,
            self.my_retail_volumes
        )
        return data

    def add(self, account):
        return self

    def update(self):
        """
        """
        self.ret_data = self._account.auth_connect(
            self.__MY_MAL_UPDATE_URL, data=self.to_xml())
        print(self.ret_data)
        assert self.ret_data == 'Updated'

    def delete(self):
        """
        """
        self.ret_data = self._account.auth_connect(
            self.__MY_MAL_UPDATE_URL, data='')
        print(self.ret_data)
        assert self.ret_data == 'Deleted'

    def __getattr__(self, name):
        return getattr(self.obj, name)

    def __dir__(self):
        return list(set(dir(type(self)) + list(self.__dict__.keys()) + dir(self.obj)))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(other) == hash(self)
        if isinstance(other, self.obj.__class__):
            return hash(other) == hash(self.obj)
        return False

    def __hash__(self):
        hash_md5 = hashlib.md5()
        hash_md5.update(str(self.id).encode())
        hash_md5.update(str(hash(self._account)).encode())
        hash_md5.update(b'MyManga')
        return int(hash_md5.hexdigest(), 16)

    def __repr__(self):
        title = '' if self._title is None else " '{0:s}'".format(self._title)
        return "<{0:s}{1:s} of account '{2:s}' id={3:d}>".format(self.__class__.__name__, title, self._account._username, self._id)
