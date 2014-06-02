from __future__ import print_function

""" 
This module provides an object-oriented event handling framework.  In this 
framework, events are registered by classes and then broadcasted by individual 
objects.  Listening for events from specific objects is made easy.

The most important parts of this framework are:

    Dispatcher -- base class that provides event handling functionality.
    event -- decorator that register events in Dispatcher subclasses.

A simple example of the framework in use:

    >>> class Button (Dispatcher):
            @event
            def on_press(self):
                print('Calling internal handler.')

    >>> button = Button()
    >>> button.connect(on_press=lambda: print('Calling external observer.'))
    >>> button.handle('on_press')
    Calling internal handler.
    Calling external observer.

The event decorator is used to register new events.  The name of the event will 
be taken from the name of the decorated method, and the method itself will be 
used as the internal handler for that type of event.  The internal handler can 
be bypassed by using notify() instead of handle():

    >>> button.notify('on_press')
    Calling external observer.

Strong error checking is possible because events are registered when the class
is created.  Exceptions are thrown if you attempt any of the following:

1. Connect to an undefined event.
2. Handle an undefined event.
3. Connect an observer that doesn't have the same argument signature as the 
   internal handler. 
4. Handle an event without providing the arugments expected by the internal 
   handler.
"""

import six
import inspect
import collections

def set_docstring_formatter(formatter):
    """ 
    Set the function used to format event docstrings.

    The formatter argument can either be a function which accepts a dictionary 
    of registered events (i.e. mapping event names to EventMetadata objects) or 
    the name of one of the builtin formatters:

    * "pretty" -- Easier to read in the terminal, used by default.
    * "sphinx" -- More verbose, but valid restructured text.
    """
    DispatcherMetaclass.set_docstring_formatter(formatter)

def pretty_docstring_formatter(cls, registered_events):
    """ 
    Use a human-readable format to display information about the given events.
    """

    events_docstring = "Events\n------\n"

    for event, metadata in registered_events.items():
        events_docstring += event + format_arg_spec(metadata) + '\n'
        events_docstring += format_description(metadata, 4) + '\n\n'

    if registered_events:
        events_docstring = events_docstring[:-2]
    else:
        events_docstring += "None defined."

    return events_docstring

def sphinx_docstring_formatter(cls, registered_events):
    """ 
    Use a strict restructured-text format the display information about the 
    given events.  This is less readable that the "pretty" format, but it is 
    rendered nicely by Sphinx.  If you want to make sphinx documentation, put 
    these lines in your configuration file:

    >>> import kemepo
    >>> kemepo.set_docstring_formatter('sphinx')
    >>> import your_dispatcher_subclasses
    """

    events_docstring = ":events:\n"

    for event, metadata in registered_events.items():
        events_docstring += '    **' + event + '**' 
        events_docstring += format_arg_spec(metadata) + '\n'
        events_docstring += format_description(metadata, 8) + '\n\n'

    if registered_events:
        events_docstring = events_docstring[:-2]
    else:
        events_docstring += "    None defined."

    return events_docstring

def format_arg_spec(metadata):
    """ 
    Return a string representing the arguments taken by the handler for the 
    given event.  This is meant to be used by the docstring formatters.
    """

    if metadata.arg_spec is None:
        return ""

    results = []

    arguments = metadata.arg_spec.args
    defaults = metadata.arg_spec.defaults
    varargs = metadata.arg_spec.varargs
    kwargs = metadata.arg_spec.keywords

    num_arguments = len(arguments)
    num_defaults = len(defaults) if defaults is not None else 0

    for index, argument in enumerate(arguments):
        if index == 0 and argument == 'self':
            continue

        default_index = index - num_arguments + num_defaults
        if default_index >= 0:
            argument += '={}'.format(defaults[default_index])

        results.append(argument)

    if varargs is not None:
        results.append('*' + varargs)

    if kwargs is not None:
        results.append('**' + kwargs)

    if results:
        return ' : ' + ', '.join(results)
    else:
        return ''

def format_description(metadata, indent=4):
    """ 
    Return a properly indented paragraph describing the given event.  This is 
    meant to be used by the docstring formatters.
    """

    import textwrap

    options = dict(
            initial_indent=' ' * indent, subsequent_indent=' ' * indent)

    description = metadata.doc_string.strip()
    description = description.replace(' \n', '\n')
    description = textwrap.fill(description, width=75, **options)

    return description


class DispatcherMetaclass (type):
    """ 
    Instantiate Dispatcher subclasses.

    This class has two primary roles:

        1. Register events marked by the event() decorator.
        2. Generate docstring based on the registered events.

    This first role is just a technical detail.  Decorators are a convenient 
    way to specify events to register, but they can't actually register events 
    because they're invoked before the class has been created.  So instead they 
    just label the methods, and the metaclass does the real registration.

    The second role is a convenience.  If you put the string '{events}' in the 
    docstring of a Dispatcher subclass, it will be replaced at runtime by a 
    description of the events registered in that subclass.
    """

    def __init__(cls, name, bases, dict):
        """ 
        Register events and build a docstring for Dispatcher subclasses.
        """
        super(DispatcherMetaclass, cls).__init__(name, bases, dict)
        cls._events = collections.OrderedDict()

        # Register events that were labeled with the 'event' decorator.  Take 
        # care to add events in the same order they were defined (for 
        # documentation purposes).

        events = []

        for key, member in dict.items():
            if hasattr(member, '_event_id'):
                events.append((member._event_id, key, member))

        for id, key, member in sorted(events):
            cls.register_event(key, member)

        # Automatically add these events to the class doc-string.

        class_docstring = inspect.getdoc(cls) or ""
        registered_events = cls.get_registered_events()
        events_docstring = cls.docstring_formatter(registered_events)
        cls.__doc__ = class_docstring.format(events=events_docstring)

    @classmethod
    def set_docstring_formatter(cls, formatter):
        try:
            builtin_formatters = cls.builtin_docstring_formatters
            cls.docstring_formatter = builtin_formatters[formatter]
        except KeyError:
            cls.docstring_formatter = formatter

    # Built-in Docstring Formatters (fold)
    builtin_docstring_formatters = {
            'sphinx': sphinx_docstring_formatter,
            'pretty': pretty_docstring_formatter,
    }

    docstring_formatter = builtin_docstring_formatters['pretty']


@six.add_metaclass(DispatcherMetaclass)
class Dispatcher (object):
    """ 
    Provide event handling functionality.  Meant to be subclassed.

    Only subclasses of Dispatcher can register and broadcast events.  
    Registration of events is mostly done using the event decorator, but can 
    also be done manually.  Each type of event can be associated with one 
    internal handler and any number of external observers.  The internal 
    handler must be specified when the event is registered (e.g. using the 
    event decorator) while external observers can be added or removed at any 
    time using connect() and disconnect().

    Two methods are provided to broadcast events: handle() and notify().  The 
    former invokes the internal handler and the external observers, while the 
    latter only invokes the external observers.

    Note that you can include documentation for every event registered to a 
    Dispatcher subclass by adding the string '{{events}}' to the subclass's 
    docstring.  This will be replaced by a informative message at runtime.  
    This is useful both for interactive usage and for Sphinx documentation.
    """

    def __init__(self):
        """ Default constructor.  Be sure to call in subclasses. """
        self._observers = collections.defaultdict(lambda: [])

    @classmethod
    def register_event(cls, event, handler=None):
        """ 
        Register the given event name.
        
        Typically you would not directly call this method.  Instead you would 
        use the event() decorator to define events from methods.

        If a handler is given, it will be set as the internal handler for this 
        event.  The internal handler is invoked before any external observers 
        when this event is triggered.  The internal handler is also used for 
        error-checking and documentation purposes, so it is good to provide one 
        even if it doesn't do anything.
        """
        cls._events[event] = EventMetadata(handler)

    @classmethod
    def get_registered_events(cls):
        """ 
        Return a list of all the events that have been registered with 
        this class.  This list will include events defined in parent classes, 
        and will be in the same order that the events were defined in.
        """
        events = collections.OrderedDict()
        for base in reversed(inspect.getmro(cls)):
            try: events.update(base._events)
            except AttributeError: pass
        return events

    @classmethod
    def get_registered_event_metadata(cls, event):
        """ 
        Return the metadata for the given event.  If the given event has 
        not been defined for this class, a TypeError is raised.
        """
        try:
            return cls.get_registered_events()[event]
        except KeyError:
            message = "Event '{}' not registered with '{}'."
            raise TypeError(message.format(event, cls.__name__))

    @classmethod
    def list_registered_events(cls):
        """ Print out every event registered by this class.  This is meant to 
        make debugging easier. """

        native = cls._events.keys()
        inherited = []

        for base in inspect.getmro(cls):
            if issubclass(base, Dispatcher):
                inherited += base._events.keys()

        print("Native events:", native)
        print("Inherited events:", inherited)

    def handle(self, event, *args, **kwargs):
        """ 
        Handle the given event.

        This invokes the internal handler for this event and any external 
        observers attached to this event using connect().
        """

        metadata = self.get_registered_event_metadata(event)
        metadata.validate_arguments(args, kwargs)

        if metadata.handler is not None:
            metadata.handler(self, *args, **kwargs)

        for observer in self._observers[event]:
            observer(*args, **kwargs)

    def notify(self, event, *args, **kwargs):
        """ 
        Notify observers about the given event.

        Unlike handle(), this method doesn't invoke the internal handler for 
        the given event.  In other words, it only invokes external observers 
        attached to the event.  This is a useful distinction when you're trying 
        to avoid infinite loops, but otherwise handle() should be preferred.
        """
        metadata = self.get_registered_event_metadata(event)
        metadata.validate_arguments(args, kwargs)

        for observer in self._observers[event]:
            observer(*args, **kwargs)

    def connect(self, *observer_objects, **observer_callbacks):
        """ 
        Attach observers to events.

        This method is very flexible in the arguments it takes.  The keyword 
        arguments are the simpler case.  These arguments are expected to be 
        simple 'event=callback' pairs.  The callback will then be invoked 
        whenever the event is triggered, until it is disconnected.  An 
        exception will be thrown if the specified event isn't registered.
        
        The regular arguments are more complicated.  These are taken to be 
        objects with methods that are meant to be observers.  In particular, a 
        method is taken to be an observer if its name matches the name of an 
        event registered with this dispatcher.  Every such method found will be 
        invoked whenever its corresponding event is triggered.

        If an internal handler was specified when the event was registered (the 
        usual case), every observer is check to make sure it takes the same 
        arguments as that handler.  This is a useful way to catch programming 
        mistakes.  Even if the internal handler doesn't do anything, it can 
        still help catch errors in the observers.
        """
        for object in observer_objects:
            for event in self.get_registered_events():
                try: observer = getattr(object, event)
                except AttributeError: continue
                metadata = self.get_registered_event_metadata(event)
                metadata.validate_observer(observer)
                self._observers[event].append(observer)

        for event, observer in observer_callbacks.items():
            metadata = self.get_registered_event_metadata(event)
            metadata.validate_observer(observer)
            self._observers[event].append(observer)

    def disconnect(self, observer):
        """ 
        Disconnect the given observer from any events it may be connected to.
        """
        for event in self._observers:
            try: self._observers[event].remove(observer)
            except ValueError: pass

            try:
                sub_handler = getattr(observer, event)
                self._observers[event].remove(sub_handler)
            except (AttributeError, ValueError): pass


class EventMetadata (object):
    """ 
    Store information about a registered event.

    The information stored in this object is used in almost every aspect of 
    this module.  A brief overview of this information is given below.  The 
    name of the event is conspicuously not included.  This is because 
    dispatchers store event metadata in dictionaries where the keys are the 
    event names, so storing the names again here would be redundant.

    The internal handler:
        Called before any observers when the event is being handled.

    The handler's argument specification:
        Used the validate external observers.

    The documentation for the event:
        Used to add event info to Dispatcher docstrings.  This documentation 
        usually comes from the docstring of the internal handler.
    """

    def __init__(self, handler=None):
        """ 
        Construct event metadata from a handler function.
        """
        self.handler = handler

        if handler is not None:
            self.arg_spec = inspect.getargspec(handler)
            self.doc_string = inspect.cleandoc(handler.__doc__ or "")
        else:
            self.arg_spec = None
            self.doc_string = ""

    def validate_arguments(self, args, kwargs):
        """ 
        Raise an exception if the given arguments are not compatible with 
        the handler for this event.

        This method is currently left unimplemented, because an exception will 
        be thrown anyway once the handler is called with the wrong arguments.  
        I left this machinery in because I think more stringent error-checking 
        might be useful in the future.
        """
        pass

    def validate_observer(self, observer):
        """ 
        Raise an exception if the given observer takes different arguments 
        that the internal handler for this type of event.
        """
        if self.arg_spec is None:
            return

        observer_spec = inspect.getargspec(observer)
        observer_args = observer_spec.args
        observer_defaults = observer_spec.defaults
        observer_varargs = observer_spec.varargs
        observer_kwargs = observer_spec.keywords

        event_args = self.arg_spec.args
        event_defaults = self.arg_spec.defaults
        event_varargs = self.arg_spec.varargs
        event_kwargs = self.arg_spec.keywords

        # Remove the 'self' argument from methods that are presumably bound.

        if observer_args and observer_args[0] == 'self':
            observer_args = observer_args[1:]
        if event_args and event_args[0] == 'self':
            event_args = event_args[1:]

        # Make sure this observer takes the right number of arguments.

        if len(event_args) != len(observer_args):
            message = "Observer takes {} arguments, {} expected."
            raise TypeError(message.format(observer_args, event_args))

        if (event_varargs is not None) and (observer_varargs is None):
            message = "Observer expected to take variable arguments."
            raise TypeError(message)

        if (event_kwargs is not None) and (observer_kwargs is None):
            message = "Observer expected to take keyword arguments."
            raise TypeError(message)



def event(handler):
    """ Register a new type of event.

    New events can be registered by providing a handler function.  The name of 
    the function is used as the name of the event, and the function itself is 
    setup to be called whenever the event needs to be handled.  This decorator 
    makes it easy register events from method in Dispatcher subclasses.

    >>> class Button (Dispatcher):
            @event
            def on_press(self):
                print('Calling internal handler.')

    Methods that get decorated by event() become "internal handlers", distinct 
    from "external observers" that can be attached later on using connect().  
    When an event is triggered, the handler for that event is always called 
    before any observers.

    Technical detail: This decorator can't actually register the new event, 
    because it is called before the class is created.  Instead, it just marks 
    the method so that a new event will be created when the class is created.  
    The actual event registration is handled by DispatcherMetaclass. """

    try: event.counter += 1
    except AttributeError: event.counter = 0
    handler._event_id = event.counter
    return handler

