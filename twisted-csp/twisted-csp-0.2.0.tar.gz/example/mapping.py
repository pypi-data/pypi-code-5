from csp import Channel, alts, CLOSED

import csp.impl.operations as op


def main():
    i = Channel()
    def m(x):
        y = x * 2
        print "\t\t\t", x, "=>", y
        return y
    o = op.map_from(m, i)

    for x in range(10):
        result = yield alts([[i, x], o])
        if result.value == CLOSED: # write
            print x
        else:
            print "\t", result.value
        # print result
