__author__ = 'thunder'

from flask import Flask as OrigFlask, request
from .endpoint import Endpoint
from helpers import wraps


class Flask(OrigFlask):

    # Для чистого роутинга. Вдруг кому пригодится
    froute = OrigFlask.route


    def route(self, rule, **options):

        """
        Роутим прям как во фласке.
        """

        def registrator(func):

            # У нас будет правило: 1 метод - 1 эндпоинт.
            if 'methods' in options:
                method = options['methods'][0]

            else:
                method = 'GET'

            wrapped = self.register_endpoint(rule, func, options.get('name'), method)

            return wrapped

        return registrator


    def register_endpoint(self, rule, func, endpoint_name=None, method='GET'):

        endpoint_name = endpoint_name or func.__name__

        endpoint = Endpoint(func)

        wrapped = self._arg_taker(endpoint)

        self.add_url_rule(rule,
                          "%s.%s" % (endpoint_name, method),
                          wrapped, methods=[method])

        return wrapped


    def _arg_taker(self, func):

        """
        Эта функция будет забирать аргументы из формы. Такие дела.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):

            for key_name, arg_object in func.__annotations__.items():

                if arg_object.multiple:
                    kwargs[key_name] = request.args.getlist(key_name)

                else:
                    kwargs[key_name] = request.args.get(key_name)

            return func(*args, **kwargs)

        return wrapper