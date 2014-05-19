from floraconcierge.client.types import Object


class Currency(Object):
    def __init__(self, *args, **kwargs):
        super(Currency, self).__init__(*args, **kwargs)

    def round(self, value, decimals=0):
        multiplier = 10 ** decimals

        return int(value * multiplier) / multiplier

    def _format(self, value):
        return self.format % value

    def convert(self, value):
        return self._format(self.convert_float(value))

    def convert_float(self, value):
        return self.round(self.usdvalue * value, 2)
