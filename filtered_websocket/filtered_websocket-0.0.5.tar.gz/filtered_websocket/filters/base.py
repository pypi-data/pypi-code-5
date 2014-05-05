"""
FilterBase and FilterMeta allow for the simple creation of a filter chains.
Any class that inherits from a child of FilterBase and FilterMeta
will have its filter method called upon run being executed from its parent class.

Ex:

>>> class A(FilterBase):
>>>     class __metaclass__(FilterMeta):
>>>         pass

>>> Class B(A):
>>>     @classmethod
>>>     def filter(cls, web_socket_instance):
>>>        print("foo")

>>> Class C(A):
>>>     @classmethod
>>>     def filter(cls, web_socket_instance):
>>>         print("bar")

>>> A.run(web_socket_instance)
foo
bar

"""


class FilterBase(object):
    @classmethod
    def run(cls, web_socket_instance, data=None):
        for filter in cls._filters:
            filter.filter(web_socket_instance, data)

    @classmethod
    def filter(cls, web_socket_instance, data=None):
        raise NotImplementedError


class FilterMeta(type):
    def __init__(self, name, type, other):
        try:
            self.__class__._filters.append(self)
        except AttributeError:
            # Anything defined here will only be applied to the class which
            # inherits from FilterBase
            self.__class__._filters = []


class WebSocketDataFilter(FilterBase):

    class __metaclass__(FilterMeta):
        pass


class WebSocketMessageFilter(FilterBase):

    class __metaclass__(FilterMeta):
        pass


class WebSocketDisconnectFilter(FilterBase):

    class __metaclass__(FilterMeta):
        pass
