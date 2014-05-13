from django.test import TestCase
from bottrap.middleware import BotTrapMiddleware
from bottrap.views import honeypot


class BotTrapTestCase(TestCase):
            
    def test_middleware(self):
        
        class FakeRequest(object):
            ip = "foo.foo.foo.foo"
            
            META = {
                "REMOTE_ADDR": ip
            }
        
        request = FakeRequest()        
        response = BotTrapMiddleware().process_request(request)
        self.assertEqual(response, None)
        
        response = honeypot(request)
        self.assertEqual(response.status_code, 200)        
        
        response = BotTrapMiddleware().process_request(request)
        self.assertEqual(response.status_code, 403)
        
        