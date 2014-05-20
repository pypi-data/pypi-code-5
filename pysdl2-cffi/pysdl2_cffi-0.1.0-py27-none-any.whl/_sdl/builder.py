# Quick, dirty way to generate wrapper functions by iterating over cffi's
# parsed declarations.

import os.path
import cffi.model

from . import cdefs, helpers

def is_primitive(arg):
    """Return true if arg is primitive or primitive*"""
    if hasattr(arg, 'totype'):
        arg = arg.totype # a pointer
    if hasattr(arg, 'ALL_PRIMITIVE_TYPES') and \
        arg.get_c_name() in arg.ALL_PRIMITIVE_TYPES:
        print "primitive %s" % (arg.get_c_name())
        return True
    print "not primitive %s" % (arg.get_c_name())
    return False

def treatment(name, declaration):
    for i, arg in enumerate(declaration.args):
        c_name = arg.get_c_name()
        if is_primitive(arg):
            yield ('pass', arg, None)
        elif i == 0 and c_name.startswith("SDL_") and c_name.endswith('*'):
            yield ('self', arg, None)
        elif c_name.endswith('*'):
            yield ('new', arg, True)
        else:
            yield('', arg, None)

class IndentedWriter(object):
    def __init__(self, writer):
        self.writer = writer
        self.level = 0
        self.indentation = "    "

    def write(self, msg):
        self.writer.write(self.indentation * self.level)
        self.writer.write(msg)
        self.writer.write("\n")

    def indent(self):
        self.level += 1

    def dedent(self):
        self.level -= 1

def handle_enum(output, declaration_name, declaration):
    if not hasattr(declaration, "enumerators"):
        # it might be an anonymous struct
        return
    for name in declaration.enumerators:
        output.write("%s = _LIB.%s" % (name, name))
    output.write("")

def handle_struct(output, declaration_name, declaration):
    output.write("class %s(Struct): pass" % declaration.name)

STRING_TYPES = ["char *", "char const *"]

def handle_function(output, declaration_name, declaration):
    fname = declaration_name.split(' ')[1]

    arg_names  = ["a%d" % i for i in range(len(declaration.args))]
    arg_vars = ', '.join(arg_names)
    output.write("def %s(%s):" % (fname, arg_vars))
    output.indent()
    output.write('"""' + declaration.get_c_name().replace("(*)", " " + fname) + '"""')
    output.write("rc = _LIB.%s(%s)" % (fname,
                                       ', '.join(["unbox(%s)" % name
                                                  for name in arg_names])))
    if declaration.result.get_c_name() in STRING_TYPES:
        output.write("return ffi.string(rc)")
    else:
        output.write("return rc")
    output.dedent()
    output.write("")
    return

    returning = []
    for i, (action, arg, returns) in enumerate(treatment(fname, declaration)):
        if action in ("pass", "self"):
            output.write("c_args[%d] = args[%d]" % (i, i))
        elif action == "new":
            output.write("c_args[%d] = ffi.new(%s)" % (i, repr(arg.get_c_name())))

            if returns:
                if isinstance(arg.totype, cffi.model.StructType):
                    # later, wrap structs.
                    returning.append("c_args[%d]" % (i,))
                else:
                    returning.append("c_args[%d][0]" % (i,))

        else:
            output.write("c_args[%d] = None" % (i, ))

    output.write("rc = _LIB.%s(*c_args)" % (fname,))

    if not returning:
        if declaration.result.get_c_name() == "char *":
            output.write("return ffi.string(rc)")
        else:
            output.write("return rc")
    else:
        if len(returning) == 1:
            output.write("return %s" % returning[0])
        else:
            output.write("return (" + ", ".join(returning) + ")")

    output.dedent()
    output.write("")

def generate(output):
    """
    Automatically generate libSDL2 wrappers by following some simple rules.
    Only used during build time.
    """
    declarations = cdefs.ffi._parser._declarations
    output = IndentedWriter(output)
    for declaration_name in sorted(declarations):
        declaration_kind, declaration_n = declaration_name.split(" ")
        if declaration_kind == "function":
            handle_function(output,
                declaration_name,
                declarations[declaration_name])

        elif declaration_kind in ("struct", "union"):
            handle_struct(output,
                declaration_name,
                declarations[declaration_name])

        elif declaration_kind in ("anonymous",):
            handle_enum(output,
                        declaration_name,
                        declarations[declaration_name])

        else:
            print(declaration_name)

        # XXX do something about typedefs that are the friendly struct names

        continue

        # XXX unreachable code:
        # The below may become a higher-level wrapper:

        fname = declaration_name.split(' ')[1]

        # Skip manually written helpers:
        if hasattr(helpers, fname):
            continue

        declaration = declarations[declaration_name]

        if declaration.args:
            output.write("def %s(*args):" % fname)
        else:
            output.write("def %s():" % fname)

        output.indent()
        output.write('"""' + declaration.get_c_name().replace("(*)", " " + fname) + '"""')
        output.write("c_args = %s" % (repr([None]*len(declaration.args))))

        returning = []
        for i, (action, arg, returns) in enumerate(treatment(fname, declaration)):
            if action in ("pass", "self"):
                output.write("c_args[%d] = args[%d]" % (i, i))
            elif action == "new":
                output.write("c_args[%d] = ffi.new(%s)" % (i, repr(arg.get_c_name())))

                if returns:
                    if isinstance(arg.totype, cffi.model.StructType):
                        # later, wrap structs.
                        returning.append("c_args[%d]" % (i,))
                    else:
                        returning.append("c_args[%d][0]" % (i,))

            else:
                output.write("c_args[%d] = None" % (i, ))

        output.write("rc = _LIB.%s(*c_args)" % (fname,))

        if not returning:
            if declaration.result.get_c_name() == "char *":
                output.write("return ffi.string(rc)")
            else:
                output.write("return rc")
        else:
            if len(returning) == 1:
                output.write("return %s" % returning[0])
            else:
                output.write("return (" + ", ".join(returning) + ")")

        output.dedent()
        output.write("")

header = """# Automatically generated wrappers.
# Override by adding wrappers to helpers.py.
from .dso import ffi, _LIB
from .structs import Struct, unbox

"""

api = ["""# API
import apipkg

exports = """, """

ns_dict = dict((s, '_sdl.renamed:%s' % s)
               for s in exports if not s.startswith('_'))
ns_dict['image'] = '_sdl_image.renamed'

apipkg.initpkg(__name__, ns_dict)
"""]


def go():
    output_filename = os.path.join(os.path.dirname(__file__), "autohelpers.py")
    with open(output_filename, "w+") as output:
        output.write(header)
        generate(output)

    import pprint
    import _sdl.renamed
    exports = pprint.pformat(sorted(dir(_sdl.renamed)))
    api_filename = os.path.join(os.path.dirname(__file__), "..", "sdl", "__init__.py")
    with open(api_filename, "w+") as output:
        output.write(exports.join(api))

if __name__ == "__main__":
    go()
