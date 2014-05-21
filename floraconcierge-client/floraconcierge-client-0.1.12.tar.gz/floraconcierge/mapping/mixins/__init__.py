from floraconcierge.client.types import Object


class Collection(Object, list):
    def __init__(self, *args, **kwargs):
        super(Collection, self).__init__(*args, **kwargs)

        self.extend(self.items)
