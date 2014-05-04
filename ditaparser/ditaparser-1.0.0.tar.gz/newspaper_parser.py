# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import unittest
import datetime

siteurl = "http://www.dt.co.kr/contents.htm?article_no=2014041402012176788001"


class CannotFindException(Exception):
    def __init__(self):
        super(Exception, self).__init__()

    def __str__(self):
        return "Cannot find string for end in target string"


class DateInfo:
    ThisYear = '2014'


class News(object):
    def __init__(self, targeturl):
        html_source = urllib.request.urlopen(targeturl).read()
        self.__parsed_gisa = BeautifulSoup(html_source)
        self.__title = self.find_title()
        self.__imgsrc = self.find_thumbnail()
        self.__body = self.find_body()

    @property
    def imgsrc(self):
        return self.__imgsrc


    @property
    def title(self):
        return self.__title

    @property
    def body(self):
        return self.__body

    def find_thumbnail(self):
        result = self.__parsed_gisa.findAll('img', attrs={'title': self.find_title()})
        if len(result) > 0:
            return result[0]['src']
        else:
            return "http://3.bp.blogspot.com/-hHVMQn9Q-f8/U0x2oc4HoII/AAAAAAAAF8Q/L0T_J_BGJJc/s1600/Screen+Shot+2014-04-15+at+8.58.31+AM.png"

    def find_title(self):
        result = self.__parsed_gisa.findAll('div', attrs={'id': 'news_names'})
        return result[0].find('h1').text

    def find_body(self):
        result = self.__parsed_gisa.findAll('div', attrs={'id': 'NewsAdContent'})
        return result[0].text

    def find_header(self):
        result = self.__parsed_gisa.findAll('div', attrs={'id': 'news_names'})
        return result[0].text


class StringParse(object):
    def __init__(self, targetString):
        self.__targetString = targetString

    def parse_string_inner(self, start, end):
        inner_strings = list()
        positions_of_startstring = self.search_start_string(start)
        print(positions_of_startstring)
        for position in positions_of_startstring:
            # print "start position:",position
            result = self.search_end_string(self.__targetString[position:], end)
            print(">>",result)
            inner_strings.append(result)

        return inner_strings

    def search_start_string(self, start):
        output = list()
        for index in range(0, len(self.__targetString)):
            if self.__targetString[index] == start:
                output.append(index + len(start))
        return output

    def search_end_string(self, string_from_start, end):
        for index in range(0, len(string_from_start)):
            if string_from_start[index] == end:
                return string_from_start[:index]

        raise Exception("Cannot find endstring")
        return None


class Test_StringParse(unittest.TestCase):
    def setUp(self):
        self.targetString = "[2014년 04월 07일자 1면 기사]"

    def test_parse1(self):
        sp = StringParse(self.targetString)
        result = sp.parse_string_inner("2014", "일자")
        print(result)

        for item in result:
            print(item)

# "[%Y년 %m월 %d일자 21면 기사]"



if __name__ == "__main__":
    unittest.main()
    # news = News(siteurl)
    # print(news.imgsrc)
    # print(news.title)
    # print(news.body)
    # print(news.date)


