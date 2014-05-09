# -*- coding: utf-8 -*-

#  Copyright 2014 Jean-Francois Paris
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.  If not, see <http://www.gnu.org/licenses/>.

import requests
from lxml import html
from decimal import Decimal
from re import sub
import time
import random

zopa_url = "https://secure2.zopa.com/login"

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:29.0) Gecko/20100101 Firefox/29.0"

class ZopaException(Exception):
    pass

class ZopaExceptionSiteChanged(ZopaException):
    pass


class ZopaClient(object):

    def __init__(self, email, password, security_questions, natural=True):
        """Initialise the Zopa client

        The init method takes a dict that contains the answers to the security questions used by Zopa
        during the authentication process. The key of the dictionary are as follow

        _security_questions  = {
            "FIRST_SCHOOL": "xxx",
            "LAST_SCHOOL": "xxx",
            "PLACE_OF_BIRTH": "xxx"
        }

        :param str email: email address for the account
        :param str password: password for the account
        :param dict security_questions: dict mapping the three expected security questions to their answers
        :param boolean natural: when true, the object behave naturally and pauses between requests
        """
        self._email = email
        self._password = password
        self._security_questions = security_questions
        self._natural = natural
        self._connected = False
        self._dashboard_url = None

        # if in natural mode, we initiate the random number generator
        if self._natural:
            random.seed()

    def _get_http_helper(self):
        """Returns a helper function that allows lxml form processor to post using requests"""

        def helper(method, url, value):
            if not url:
                raise ValueError("cannot submit, no URL provided")
            if method == 'GET':
                return self._session.get(url, value)
            else:
                return self._session.post(url, value)

        return helper

    def _sleep_if_needed(self):
        """Sleep for a random amount of time between 2 and 10 seconds

        This method is used to make our behaviour look more human and avoid overloading Zopa's server
        """
        if self._natural:
            #if in natural mode we sleep for some time
            time.sleep(random.randint(2, 10))

    def _extract_url(self, tree):
        """Extract and save the main urls

        This method shall be called once after connection in order to
        avoid having to seek for the URL at a later stage
        """
        # noinspection PyAttributeOutsideInit
        self._exit_url = tree.cssselect(".signin a")[0].get("href")
        self._loanbook_url = tree.cssselect("#lending_my_loan_book a")[0].get("href")
        self._account_url = tree.cssselect("#lending_account a")[0].get("href")
        self._statement_url = "https://secure2.zopaclient.com/lending/statements"

    def connect(self):
        """Connect the client from Zopa"""
        # initiate the browser
        self._session = requests.Session()
        self._session.headers = {'User-agent': user_agent}
        self._session.verify = True

        # pull zopaclient signup page
        page = self._session.get(zopa_url)
        self._sleep_if_needed()

        # fill the signup form
        tree = html.fromstring(page.text, base_url=page.url)
        form = tree.forms[0]
        form.fields["email"] = self._email
        form.fields["password"] = self._password
        page = html.submit_form(form, open_http=self._get_http_helper())
        self._sleep_if_needed()

        # check if we have landed on the secret verification page
        url = page.url
        if not "login/confirm" in url:
            raise ZopaExceptionSiteChanged("Unexpected page")

        # fill the idea verification form
        tree = html.fromstring(page.text, base_url=page.url)
        form = tree.forms[0]
        form.fields["answer"] = self._security_questions[form.fields["question"]]
        page = html.submit_form(form, open_http=self._get_http_helper())

        self._sleep_if_needed()

        # check if we have landed on the dashboard page
        url = page.url
        if not "/dashboard" in url:
            raise ZopaExceptionSiteChanged("Unexpected page")()

        self._connected = True
        self._dashboard_url = url
        tree = html.fromstring(page.text, base_url=page.url)
        tree.make_links_absolute(page.url)
        self._extract_url(tree)

    def disconnect(self):
        """Disconnect the client from Zopa"""
        # call the logout url
        page = self._session.get(self._exit_url)
        url = page.url
        if not "/signed_out" in url:
            raise Exception("Failed to sign out")

        self._connected = False

    def get_loan_book(self):
        """Download and return the full loan book

        :return: loan book in csv format
        :rtype: str
        """
        page = self._session.get(self._loanbook_url)
        self._sleep_if_needed()

        tree = html.fromstring(page.text, base_url=page.url)
        form = tree.forms[0]

        # submit the two following values through the extra_values parameters
        # as they are not part of the initial form
        values = {"_template$MainControl$Content$MyLoanBookControl$btnDownloadCSV.x": "132",
                  "_template$MainControl$Content$MyLoanBookControl$btnDownloadCSV.y": "7"}

        page = html.submit_form(form, extra_values=values, open_http=self._get_http_helper())
        return page.text

    def get_statement(self, year, month):
        """Download and return the monthly statement for a given period

        :param int year: year for which the statement is required
        :param int month: month within the year for which the statement is required
        :return: statement in csv format
        :rtype: str
        """
        page = self._session.get(self._statement_url)
        self._sleep_if_needed()

        tree = html.fromstring(page.text, base_url=page.url)
        form = tree.forms[0]

        form.fields["date[month]"] = str(month) if type(month) == int else month
        form.fields["date[year]"] = str(year) if type(year) == int else year

        page = html.submit_form(form, open_http=self._get_http_helper())
        return page.text


    def get_account_summary(self):
        """Get the account summary

        :return: summary of current account
        :rtype: dict
        """

        page = self._session.get(self._account_url)
        self._sleep_if_needed()

        results = {}

        tree = html.fromstring(page.text, base_url=page.url)

        summary_items = tree.cssselect(".result .important strong")
        results["Total earnings"] = Decimal(sub(r'[^\d\-.]', '', summary_items[0].text.strip(u'£')))
        results["Zopa total"] = Decimal(sub(r'[^\d\-.]', '', summary_items[1].text.strip(u'£')))
        results["Total paid in"] = Decimal(sub(r'[^\d\-.]', '', summary_items[2].text.strip(u'£')))
        results["Total paid out"] = Decimal(sub(r'[^\d\-.]', '', summary_items[3].text.strip(u'£')))

        summary_items = tree.cssselect(".lending-offers-summary td.number")
        results["Not offered"] = Decimal(sub(r'[^\d\-.]', '', summary_items[0].text.strip(u'£')))
        results["Fees not yet deducted"] = Decimal(sub(r'[^\d\-.]', '', summary_items[2].text.strip(u'£')))
        results["Offered"] = Decimal(sub(r'[^\d\-.]', '', summary_items[4].text.strip(u'£')))
        results["Processing"] = Decimal(sub(r'[^\d\-.]', '', summary_items[6].text.strip(u'£')))
        results["Processing - nb loans"] = Decimal(sub(r'[^\d\-.]', '', summary_items[7].text.strip(u'£')))
        results["Lent out"] = Decimal(sub(r'[^\d\-.]', '', summary_items[8].text.strip(u'£')))
        results["Lent out - nb loans"] = Decimal(sub(r'[^\d\-.]', '', summary_items[9].text.strip(u'£')))
        results["Late payment"] = Decimal(sub(r'[^\d\-.]', '', summary_items[10].text.strip(u'£')))
        results["Lent out - nb loans"] = Decimal(sub(r'[^\d\-.]', '', summary_items[11].text.strip(u'£')))
        results["Bad debt"] = Decimal(sub(r'[^\d\-.]', '', summary_items[14].text.strip(u'£')))
        results["Bad debt - nb loans"] = Decimal(sub(r'[^\d\-.]', '', summary_items[15].text.strip(u'£')))

        summary_items = tree.cssselect(".lending-offers-all-time-summary td.number")
        results["All time - Interest from borrowers"] = Decimal(sub(r'[^\d\-.]', '', summary_items[0].text.strip(u'£')))
        results["All time - Holding account interest"] = Decimal(sub(r'[^\d\-.]', '', summary_items[1].text.strip(u'£')))
        results["All time - Zopa bonuses"] = Decimal(sub(r'[^\d\-.]', '', summary_items[2].text.strip(u'£')))
        results["All time - Tell-a-friend rewards"] = Decimal(sub(r'[^\d\-.]', '', summary_items[3].text.strip(u'£')))
        results["All time - Rapid Return interest credits"] = Decimal(sub(r'[^\d\-.]', '', summary_items[4].text.strip(u'£')))
        results["All time - Rate Promise"] = Decimal(sub(r'[^\d\-.]', '', summary_items[5].text.strip(u'£')))
        results["All time - Total lender fees"] = Decimal(sub(r'[^\d\-.]', '', summary_items[6].text.strip(u'£')))
        results["All time - Bad debt"] = Decimal(sub(r'[^\d\-.]', '', summary_items[7].text.strip(u'£')))
        results["All time - Total lent out"] = Decimal(sub(r'[^\d\-.]', '', summary_items[8].text.strip(u'£')))
        results["All time - Capital returned "] = Decimal(sub(r'[^\d\-.]', '', summary_items[9].text.strip(u'£')))

        return results
