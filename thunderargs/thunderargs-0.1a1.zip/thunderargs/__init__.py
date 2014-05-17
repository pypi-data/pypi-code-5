__author__ = 'thunder'
__version__ = '0.1a1'


class Arg(object):

    """
    A request argument.
    """

    def __call__(self, dct):
        return self.validated(dct)


    def __init__(self, p_type=str, default=None, multiple=False):

        self.type = p_type
        self.default = default
        self.multiple = multiple


    def _validate(self, value):

        """Perform conversion and validation on ``value``."""

        return self.type(value)


    def validated(self, value):
        """
        Convert and validate the given value according to the ``p_type``
        Sets default if value is None
        """

        if value is None:

            if self.multiple:
                return [self.default] or [self.type()]

            return self.default or self.type()

        if self.multiple:
            return map(self._validate, value)

        return self._validate(value)




class Parser(object):

    def __call__(self, dct):

        """
        Just for simplify
        """

        return self.validated(dct)


    def __init__(self, structure):
        self.structure = structure


    def validated(self, dct):

        for key, arg_instatce in self.structure.items():
            dct[key] = arg_instatce(dct.get(key, None))

        return dct