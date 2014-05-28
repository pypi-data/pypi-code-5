__author__ = 'thunder'
__version__ = '0.1'


class Arg(object):

    """
    A request argument.
    """

    def __call__(self, value):
        return self.validated(value)


    def __init__(self, p_type=str, default=None, multiple=False, required=False,
                 validators=[], expander=None, suppress_expanding_check=False, source=None):

        if required and default:
            raise ValueError("Argument can't have default value and be required same time")

        if validators:
            for validator in validators:
                if not callable(validator):
                    raise ValueError("All validators must be callable")

        if expander and not (callable(expander) or type(expander) is dict):
            raise ValueError("Expander must be callable or dict")

        if validators and default:
            for validator in validators:
                if not validator(default):
                    raise ValueError("Default value must be valid")

        self.type = p_type
        self.default = default
        self.multiple = multiple
        self.required = required
        self.validators = validators
        self.expander = expander
        self.source = source
        self.check_expanding = not suppress_expanding_check


    def _validate(self, value):
        """Perform conversion and validation on ``value``."""

        typed_value = self.type(value)

        if self.validators:
            for validator in self.validators:
                if not validator(typed_value):
                    raise ValueError("Value is invalid")

        if self.expander:

            if type(self.expander) is dict:

                if not typed_value in self.expander and self.check_expanding:
                    raise ValueError("Can't find %s in expander" % typed_value)

                else:
                    return self.expander.get(typed_value)

            else:

                return self.expander(typed_value)

        return typed_value


    def validated(self, value):
        """
        Convert and validate the given value according to the ``p_type``
        Sets default if value is None
        """

        if value is None:

            if self.required:
                raise ValueError("Argument is required")

            if self.multiple:
                value = [self.default] if self.default is not None else [self.type()]

            else:
                value = self.default or self.type()

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