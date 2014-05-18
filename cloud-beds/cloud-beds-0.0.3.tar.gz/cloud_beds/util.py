def consumer(func):
    def start(*args,**kwargs):
        c = func(*args,**kwargs)
        next(c)
        return c
    return start
