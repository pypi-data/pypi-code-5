#!/usr/bin/env python
# Copyright (c) 2013 Amazon.com, Inc. or its affiliates.  All Rights Reserved
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
from tests.unit import unittest
from tests.unit import AWSMockServiceTestCase

from boto.jsonresponse import ListElement
from boto.ses.connection import SESConnection


class TestSESIdentity(AWSMockServiceTestCase):
    connection_class = SESConnection

    def setUp(self):
        super(TestSESIdentity, self).setUp()

    def default_body(self):
        return """<GetIdentityDkimAttributesResponse \
xmlns="http://ses.amazonaws.com/doc/2010-12-01/">
  <GetIdentityDkimAttributesResult>
    <DkimAttributes>
      <entry>
        <key>amazon.com</key>
      <value>
        <DkimEnabled>true</DkimEnabled>
        <DkimVerificationStatus>Success</DkimVerificationStatus>
        <DkimTokens>
          <member>vvjuipp74whm76gqoni7qmwwn4w4qusjiainivf6f</member>
          <member>3frqe7jn4obpuxjpwpolz6ipb3k5nvt2nhjpik2oy</member>
          <member>wrqplteh7oodxnad7hsl4mixg2uavzneazxv5sxi2</member>
        </DkimTokens>
      </value>
    </entry>
    </DkimAttributes>
  </GetIdentityDkimAttributesResult>
  <ResponseMetadata>
    <RequestId>bb5a105d-c468-11e1-82eb-dff885ccc06a</RequestId>
  </ResponseMetadata>
</GetIdentityDkimAttributesResponse>"""

    def test_ses_get_identity_dkim_list(self):
        self.set_http_response(status_code=200)

        response = self.service_connection\
                       .get_identity_dkim_attributes(['test@amazon.com'])

        response = response['GetIdentityDkimAttributesResponse']
        result = response['GetIdentityDkimAttributesResult']
        attributes = result['DkimAttributes']['entry']['value']
        tokens = attributes['DkimTokens']

        self.assertEqual(ListElement, type(tokens))
        self.assertEqual(3, len(tokens))
        self.assertEqual('vvjuipp74whm76gqoni7qmwwn4w4qusjiainivf6f',
                         tokens[0])
        self.assertEqual('3frqe7jn4obpuxjpwpolz6ipb3k5nvt2nhjpik2oy',
                         tokens[1])
        self.assertEqual('wrqplteh7oodxnad7hsl4mixg2uavzneazxv5sxi2',
                         tokens[2])


if __name__ == '__main__':
    unittest.main()
