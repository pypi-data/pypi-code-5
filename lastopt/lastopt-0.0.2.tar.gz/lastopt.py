import re
import sys
import inspect

from optparse import OptionParser
from optparse import make_option


__version__ = '0.0.2'


def to_OptionParser(options, usage=None):
    # add options, automatically detecting their -short and --long names

    single_char_prefix_re = re.compile('^[a-zA-Z0-9]_')

    optypes=[int, long, float, complex] # not type='choice' choices='a|b'
    def optype(t):
        if t is bool:
            return None
        if t in optypes:
            return t
        return "string"

    # TODO:
    # helpdict = getattr(func, 'optfunc_arghelp', {})
    helpdict = {}

    opt = OptionParser(usage)

    shortnames = set(['h'])
    for name in options.iterkeys():
        if single_char_prefix_re.match(name):
            shortnames.add(name[0])

    for original, default in options.iteritems():
        name = original
        # x_argument forces short name for argument to be x
        if single_char_prefix_re.match(name):
            short = name[0]
            name = name[2:]
            opt._custom_names[name] = original

        # or we pick the first letter from the name not already in use:
        else:
            short=None
            for s in name:
                if s not in shortnames:
                    short=s
                    break
        names = []
        if short is not None:
            shortnames.add(short)
            short_name = '-%s' % short
            names.append(short_name)

        clean_name = name.replace('_', '-')
        long_name = '--%s' % clean_name
        names.append(long_name)

        if isinstance(default, bool):
            if default:
                no_name='--no%s' % clean_name
                opt.add_option(make_option(
                    no_name,
                    action='store_false',
                    dest=name,
                    help = helpdict.get(original, 'unset %s' % long_name)))
                continue

            action = 'store_true'

        else:
            action = 'store'

        example = str(default)
        if isinstance(default, int):
            if default==sys.maxint: example = "INFINITY"
            if default==(-sys.maxint-1): example = "-INFINITY"

        help_post = ' (default: %s)' % example

        opt.add_option(make_option(*names,
            action=action,
            dest=name,
            default=default,
            help=helpdict.get(original, '') + help_post,
            type=optype(type(default))))

    return opt


def get_interface(target):
    if inspect.isclass(target):
        target = target.__init__

    args, varargs, varkw, defaultvals = inspect.getargspec(target)
    defaultvals = defaultvals or ()
    optional = dict(zip(args[-len(defaultvals):], defaultvals))

    required = args
    if inspect.ismethod(target):
        # skip bounded self argument
        required = args[1:]
    if defaultvals:
        required = required[:-len(defaultvals)]

    return required, optional


def parse(parsed, target, argv):
    required, optional = get_interface(target)

    usage = "%s %s%s" % (
        parsed,
        ' '.join('<%s>' % a for a in required),
        optional and ' [options]' or '')

    parser = to_OptionParser(optional, usage=usage)

    if len(argv) == 1 and argv[0] in ['-h', '--help']:
        parser.print_help()
        sys.exit(0)

    if len(argv) < len(required):
        print "Usage:", usage
        sys.exit(1)

    a = argv[:len(required)]
    opt, remaining = parser.parse_args(argv[len(required):])
    kw = opt.__dict__
    if remaining:
        used = argv[:-len(remaining)]
    else:
        used = argv
    parsed += ' ' + ' '.join(str(x) for x in used)
    return a, kw, parsed, remaining


def run(parsed, target, argv):
    if not isinstance(target, (tuple, list)) and not callable(target):
        # try and use as an object
        target = [getattr(target, x) for x in dir(target)
                if not x.startswith('_') and callable(getattr(target, x))]

    if isinstance(target, (tuple, list)):
        choices = dict(
            (x.__name__.lower().replace('_', '-'), x) for x in target)
        try:
            target = choices[argv[0]]
        except (KeyError, IndexError):
            def format(name, choice):
                summary = ""
                if choice.__doc__:
                    summary = choice.__doc__.strip().split('\n')[0]
                return "    %-10s%s" % (name, summary)
            print 'Usage: %s COMMAND [ARGS]\n\nThe available commands are:' % \
                parsed
            print '\n'.join(format(*item) for item in choices.iteritems())
            return
        parsed += ' %s' % argv[0]
        argv = argv[1:]

    a, kw, parsed, remaining = parse(parsed, target, argv)

    target = target(*a, **kw)

    if remaining or (target and not isinstance(target, (int, str))):
        return run(parsed, target, remaining)

    return target


def main(target):
    module = inspect.getmodule(inspect.stack()[1][0])
    if module is None or \
            module.__name__ == '<module>' or \
            module.__name__ == '__main__':
        run(sys.argv[0], target, sys.argv[1:])
    return target # for use as decorator


# Tests
###############################################################################


import unittest


class InterfaceTest(unittest.TestCase):
    def test_basic(self):
        def f(a, b, c=1, d='foo'):
            pass
        got = get_interface(f)
        self.assertEqual(got, (['a', 'b'], {'c': 1, 'd': 'foo'}))

    def test_klass(self):
        class F(object):
            def __init__(self, a, b, c=1, d='foo'):
                pass
        got = get_interface(F)
        self.assertEqual(got, (['a', 'b'], {'c': 1, 'd': 'foo'}))


class OptionParserTest(unittest.TestCase):
    def test_core(self):
        parser = to_OptionParser({'foo': 'bar'})
        argv = ['-f', 'ted']
        options, a = parser.parse_args(argv)
        self.assertEqual(options.foo, 'ted')

        parser = to_OptionParser({'num': 3})
        argv = ['--num=5']
        options, a = parser.parse_args(argv)
        self.assertEqual(options.num, 5)

        parser = to_OptionParser({'toggle': False})
        argv = []
        options, a = parser.parse_args(argv)
        self.assertEqual(options.toggle, False)
        argv = ['-t']
        options, a = parser.parse_args(argv)
        self.assertEqual(options.toggle, True)
        argv = ['--toggle']
        options, a = parser.parse_args(argv)
        self.assertEqual(options.toggle, True)

        parser = to_OptionParser({'to_email': 'bar'})
        argv = ['--to-email', 'ted']
        options, a = parser.parse_args(argv)
        self.assertEqual(options.to_email, 'ted')


class RunTest(unittest.TestCase):
    def test_list_of_functions(self):
        def m_1(a):
            return a
        def m_2(b=2):
            return b
        self.assertEqual(run('foo', [m_1, m_2], ['m-1', 3],), 3)
        self.assertEqual(run('foo', [m_1, m_2], ['m-2'],), 2)

    def test_klass(self):
        class C(object):
            def m_1(self, a):
                return a
            def m_2(self, b=2):
                return b
        c = C()
        self.assertEqual(run('foo', c, ['m-1', 3]), 3)
        self.assertEqual(run('foo', c, ['m-2']), 2)

    def test_list_of_klasses(self):
        class User(object):
            def __init__(self, user_id):
                self.user_id = user_id
            def name(self):
                return "name for user: %s" % self.user_id

        class Room(object):
            def __init__(self, room_id):
                self.room_id = room_id
            def members(self):
                return "members for room: %s" % self.room_id

        self.assertEqual(
            run('foo', [User, Room], ['user', 123, 'name']),
            'name for user: 123')


# run tests on __main__
main(unittest.main)
