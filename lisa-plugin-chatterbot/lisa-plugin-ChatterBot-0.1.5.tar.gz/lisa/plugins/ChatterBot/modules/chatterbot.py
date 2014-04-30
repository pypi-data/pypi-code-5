# -*- coding: UTF-8 -*-
from datetime import datetime
from lisa.server.plugins.IPlugin import IPlugin
import gettext

class ChatterBot(IPlugin):
    def __init__(self):
        super(ChatterBot, self).__init__()
        self.configuration_plugin = self.mongo.lisa.plugins.find_one({"name": "ChatterBot"})
        self._ = translation = gettext.translation(domain='chatterbot',
                                                   localedir=self.path,
                                                   languages=[self.configuration_lisa['lang']]).ugettext

    def getTime(self, jsonInput):
        now = datetime.now()
        return {"plugin": "ChatterBot",
                "method": "getTime",
                "body": now.strftime(self._('time'))
        }

    def sayHello(self, jsonInput):
        return {"plugin": "ChatterBot",
                "method": "sayHello",
                "body": self._('Hello. How are you ?')
        }