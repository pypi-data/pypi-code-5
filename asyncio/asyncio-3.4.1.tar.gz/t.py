def f():
    x = yield
    print('x =', repr(x))
    y = yield
    print('y =', repr(y))
g = f()
next(g)
t = (0, 1, 2, 3, 4, 5)
g.send(*t)
