
def freeze(obj, lj):
    
    name  = obj.__name__
    bases = obj.__bases__
    
    funcs = {f:lj.flatten(obj.__dict__[f])
             for f in obj.__dict__
             if callable(obj.__dict__[f])}

    bases = [str(b).split()[1][1:-2] for b in bases]

    return str([name, bases, funcs])

def defreeze(obj, lj):

    info  = eval(obj[7:])

    name  = info[0]
    bases = info[1]
    funcs = info[2]

    funcs = {f:lj.restore(funcs[f]) for f in funcs}

    globs = lj.globs()

    for i in range(len(bases)):
        base = bases[i].split('.')
        while not base[0] in globs:
            base.pop(0)

        if base:
            bases[i] = '.'.join(base)
        else:
            bases[i] = ''
        

    bases = [b for b in bases if b]

    Class = eval('type("{name}", {bases}, funcs)'.format(
             name = name,bases = str(tuple(bases)).replace("'",'')),
             globs, locals())

    return Class
