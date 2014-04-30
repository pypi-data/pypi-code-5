import sys

def main(argv):
    argv.remove(argv[0])
    for expr in argv:
        print "expr: ", expr, " = ", eval(expr)

if __name__ == "__main__":
    main(sys.argv)
