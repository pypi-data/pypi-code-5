class UncatchableException(Exception):

    def __call__(self, *args, **kwargs):
        return self.__class__(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(UncatchableException, self).__init__(*args, **kwargs)
        try:
            raise self(*args, **kwargs)
        except RuntimeError:
            # RuntimeError: maximum recursion depth exceeded
            raise self(*args, **kwargs)
