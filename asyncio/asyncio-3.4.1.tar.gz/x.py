class C:
    def __iter__(self):
        yield 1
        yield 2

    def __del__(self):
        print('__del__')

def a_generator():
    yield from C()

def main():
    for i in a_generator():
        print(i)

main()
