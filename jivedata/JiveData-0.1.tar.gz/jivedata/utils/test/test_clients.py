import unittest
from jivedata.utils import Client


class Tester(unittest.TestCase):
    def test_credentials(self):
        client = Client('', '')
        self.assertRaisesRegexp(Exception,
                                'Your client credentials are invalid',
                                client.get_token)


if __name__ == '__main__':
    unittest.main()
