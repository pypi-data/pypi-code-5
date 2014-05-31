from csp.impl.channels import Box, ManyToManyChannel as Channel
from csp import go, put, take, close

def map_from(f, ch):
    class Channel:
        def close(self):
            ch.close()

        def put(self, value, handler):
            return ch.put(value, handler)

        def take(self, handler):
            class Handler:
                def is_active(self):
                    return handler.is_active()

                def commit(self):
                    f1 = handler.commit()
                    return lambda v: f1(None if v is None else f(v))

            result = ch.take(Handler())
            if result and result.value is not None:
                return Box(f(result.value))
            else:
                return None

    return Channel()

# def map_from1(f, ch):
#     return MapFrom(f, ch)


# class DerivedChannel:
#     pass

# class DerivedHandler:
#     pass

# def map_from(f, ch):
#     out = DerivedChannel()

#     def take(self, handler):
#         h = DerivedHandler()
#         h.is_active = lambda self: handler.is_active()
#         h.commit = lambda self: lambda v: handler.commit()(
#             None if v is None else f(v))

#         result = ch.take(h)
#         if result and result.value:
#             return Box(f(result.value))
#         else:
#             return None

#     out.close = lambda self: ch.close()
#     out.put = lambda self, value, handler: ch.put(value, handler)
#     out.take = take

#     return out

def filter_from(predicate, channel, buf):
    out = Channel(buf)
    def _filter():
        while True:
            value = yield take(channel)
            if value is None:
                close(out)
                break
            if predicate(value):
                yield put(out, value)
    go(_filter())
    return out
