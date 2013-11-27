from ..vendor.lexicon import Lexicon

from .argument import Argument


def to_flag(name):
    name = name.replace('_', '-')
    if len(name) == 1:
        return '-' + name
    return '--' + name

def sort_candidate(arg):
    names = arg.names
    # TODO: is there no "split into two buckets on predicate" builtin?
    shorts = set(x for x in names if len(x.strip('-')) == 1)
    longs = set(x for x in names if x not in shorts)
    return sorted(shorts if shorts else longs)[0]

def flag_key(x):
    """
    Obtain useful key list-of-ints for sorting CLI flags.
    """
    # Setup
    ret = []
    x = sort_candidate(x)
    # Long-style flags win over short-style ones, so the first item of
    # comparison is simply whether the flag is a single character long (with
    # non-length-1 flags coming "first" [lower number])
    ret.append(1 if len(x) == 1 else 0)
    # Next item of comparison is simply the strings themselves,
    # case-insensitive. They will compare alphabetically if compared at this
    # stage.
    ret.append(x.lower())
    # Finally, if the case-insensitive test also matched, compare
    # case-sensitive, but inverse (with lowercase letters coming first)
    inversed = ''
    for char in x:
        inversed += char.lower() if char.isupper() else char.upper()
    ret.append(inversed)
    return ret


class Context(object):
    """
    Parsing context with knowledge of flags & their format.

    Generally associated with the core program or a task.

    When run through a parser, will also hold runtime values filled in by the
    parser.
    """
    def __init__(self, name=None, aliases=(), args=()):
        """
        Create a new ``Context`` named ``name``, with ``aliases``.

        ``name`` is optional, and should be a string if given. It's used to
        tell Context objects apart, and for use in a Parser when determining
        what chunk of input might belong to a given Context.

        ``aliases`` is also optional and should be an iterable containing
        strings. Parsing will honor any aliases when trying to "find" a given
        context in its input.

        May give one or more ``args``, which is a quick alternative to calling
        ``for arg in args: self.add_arg(arg)`` after initialization.
        """
        self.args = Lexicon()
        self.positional_args = []
        self.flags = Lexicon()
        self.inverse_flags = {} # No need for Lexicon here
        self.name = name
        self.aliases = aliases
        for arg in args:
            self.add_arg(arg)

    def __str__(self):
        aliases = (" (%s)" % ', '.join(self.aliases)) if self.aliases else ""
        name = (" %r%s" % (self.name, aliases)) if self.name else ""
        args = (": %r" % (self.args,)) if self.args else ""
        return "<Context%s%s>" % (name, args)

    def __repr__(self):
        return str(self)

    def add_arg(self, *args, **kwargs):
        """
        Adds given ``Argument`` (or constructor args for one) to this context.

        The Argument in question is added to the following dict attributes:

        * ``args``: "normal" access, i.e. the given names are directly exposed
          as keys.
        * ``flags``: "flaglike" access, i.e. the given names are translated
          into CLI flags, e.g. ``"foo"`` is accessible via ``flags['--foo']``.
        * ``inverse_flags``: similar to ``flags`` but containing only the
          "inverse" versions of boolean flags which default to True. This
          allows the parser to track e.g. ``--no-myflag`` and turn it into a
          False value for the ``myflag`` Argument.
        """
        # Normalize
        if len(args) == 1 and isinstance(args[0], Argument):
            arg = args[0]
        else:
            arg = Argument(*args, **kwargs)
        # Uniqueness constraint: no name collisions
        for name in arg.names:
            if name in self.args:
                msg = "Tried to add an argument named %r but one already exists!"
                raise ValueError(msg % name)
        # First name used as "main" name for purposes of aliasing
        main = arg.names[0] # NOT arg.name
        self.args[main] = arg
        # Note positionals in distinct, ordered list attribute
        if arg.positional:
            self.positional_args.append(arg)
        # Add names & nicknames to flags, args
        self.flags[to_flag(main)] = arg
        for name in arg.nicknames:
            self.args.alias(name, to=main)
            self.flags.alias(to_flag(name), to=to_flag(main))
        # Add attr_name to args, but not flags
        if arg.attr_name:
            self.args.alias(arg.attr_name, to=main)
        # Add to inverse_flags if required
        if arg.kind == bool and arg.default == True:
            # Invert the 'main' flag name here, which will be a dashed version
            # of the primary argument name if underscore-to-dash transformation
            # occurred.
            inverse_name = to_flag("no-%s" % main)
            self.inverse_flags[inverse_name] = to_flag(main)

    @property
    def needs_positional_arg(self):
        return any(x.value is None for x in self.positional_args)

    def help_for(self, flag):
        """
        Return 2-tuple of ``(flag-spec, help-string)`` for given ``flag``.
        """
        # Obtain arg obj
        if flag not in self.flags:
            raise ValueError("%r is not a valid flag for this context! Valid flags are: %r" % (flag, self.flags.keys()))
        arg = self.flags[flag]
        # Show all potential names for this flag in the output
        names = list(set([flag] + self.flags.aliases_of(flag)))
        # Determine expected value type, if any
        value = {
            str: 'STRING',
        }.get(arg.kind)
        # Format & go
        full_names = []
        for name in names:
            if value:
                # Short flags are -f VAL, long are --foo=VAL
                # When optional, also, -f [VAL] and --foo[=VAL]
                if len(name.strip('-')) == 1:
                    value_ = ("[%s]" % value) if arg.optional else value
                    valuestr = " %s" % value_
                else:
                    valuestr = "=%s" % value
                    if arg.optional:
                        valuestr = "[%s]" % valuestr
            else:
                valuestr = ""
            # Tack together
            full_names.append(name + valuestr)
        namestr = ", ".join(sorted(full_names, key=len))
        helpstr = arg.help or ""
        return namestr, helpstr

    def help_tuples(self):
        """
        Return sorted iterable of help tuples for all member Arguments.

        Sorts like so:

        * General sort is alphanumerically
        * Short flags win over long flags
        * Arguments with *only* long flags and *no* short flags will come
          first.
        * When an Argument has multiple long or short flags, it will sort using
          the most favorable (lowest alphabetically) candidate.

        This will result in a help list like so::

            --alpha, --zeta # 'alpha' wins
            --beta
            -a, --query # short flag wins
            -b, --argh
            -c
        """
        # TODO: argument/flag API must change :(
        # having to call to_flag on 1st name of an Argument is just dumb.
        # To pass in an Argument object to help_for may require moderate
        # changes?
        # Cast to list to ensure non-generator on Python 3.
        return list(map(
            lambda x: self.help_for(to_flag(x.name)),
            sorted(self.flags.values(), key=flag_key)
        ))
