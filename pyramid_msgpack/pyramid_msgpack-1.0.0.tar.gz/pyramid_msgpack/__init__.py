import umsgpack as mp


def msgpack_renderer_factory(info):
    def _render(value, system):
        value = mp.packb(value)
        request = system.get('request')
        if request is not None:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = 'application/x-msgpack'
        return value
    return _render
