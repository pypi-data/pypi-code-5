from __future__ import unicode_literals

from django.utils.encoding import force_text
from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

import six

__all__ = ('AutocompleteInterface', 'AutocompleteBase')


class AutocompleteInterface(object):
    """
    An autocomplete proposes "choices". A choice has a "value". When the user
    selects a "choice", then it is converted to a "value".

    AutocompleteInterface is the minimum to implement in a custom Autocomplete
    class usable by the widget and the view. It has two attributes:

    .. py:attribute:: values

        A list of values which
        :py:meth:`~.base.AutocompleteInterface.validate_values` and
        :py:meth:`~.base.AutocompleteInterface.choices_for_values` should use.

    .. py:attribute:: request

        A request object which
        :py:meth:`~.base.AutocompleteInterface.autocomplete_html()` should use.

    It is recommended that you inherit from :py:class:`~.base.AutocompleteBase`
    instead when making your own classes because it has taken some design
    decisions favorising a DRY implementation of
    :py:class:`~.base.AutocompleteInterface`.

    Instanciate an Autocomplete with a given ``request`` and ``values``
    arguments. ``values`` will be casted to list if necessary and both will
    be assigned to instance attributes
    :py:attr:`~AutocompleteInterface.request` and
    :py:attr:`~AutocompleteInterface.values` respectively.
    """

    def __init__(self, request=None, values=None):
        self.request = request

        if values is None:
            self.values = values
        elif (isinstance(values, six.string_types) or
                not hasattr(values, '__iter__')):
            self.values = [values]
        else:
            self.values = values

    def autocomplete_html(self):
        """
        Return the HTML autocomplete that should be displayed under the text
        input. :py:attr:`request` can be used, if set.
        """
        raise NotImplemented()

    def validate_values(self):
        """
        Return True if :py:attr:`values` are all valid.
        """
        raise NotImplemented()

    def choices_for_values(self):
        """
        Return the list of choices corresponding to :py:attr:`values`.
        """
        raise NotImplemented()

    def get_absolute_url(self):
        """
        Return the absolute url for this autocomplete, using
        autocomplete_light_autocomplete url.
        """
        try:
            return urlresolvers.reverse('autocomplete_light_autocomplete',
                args=(self.__class__.__name__,))
        except urlresolvers.NoReverseMatch as e:
            # Such error will ruin form rendering. It would be automatically
            # silenced because of e.silent_variable_failure=True, which is
            # something we don't want. Let's give the user a hint:
            raise ImproperlyConfigured("URL lookup for autocomplete '%s' "
                    "failed. Have you included autocomplete_light.urls in "
                    "your urls.py?" % (self.__class__.__name__,))


class AutocompleteBase(AutocompleteInterface):
    """
    A basic implementation of AutocompleteInterface that renders HTML and
    should fit most cases. It only needs overload of
    :py:meth:`~.base.AutocompleteBase.choices_for_request` and
    :py:meth:`~.base.AutocompleteInterface.choices_for_values` which is the
    business-logic.

    .. py:attribute:: choice_html_format

        HTML string used to format a python choice in HTML by
        :py:meth:`~.base.AutocompleteBase.choice_html`. It is formated with two
        positionnal parameters: the value and the html representation,
        respectively generated by
        :py:meth:`~.base.AutocompleteBase.choice_value` and
        :py:meth:`~.base.AutocompleteBase.choice_label`. Default is::

            <span class="div" data-value="%s">%s</span>

    .. py:attribute:: empty_html_format

        HTML string used to format the message "no matches found" if no choices
        match the current request. It takes a parameter for the translated
        message. Default is::

            <span class="div"><em>%s</em></span>

    .. py:attribute:: autocomplete_html_format

        HTML string used to format the list of HTML choices. It takes a
        positionnal parameter which contains the list of HTML choices which
        come from :py:meth:`~.base.AutocompleteBase.choice_html`. Default is::

            %s

    .. py:attribute:: add_another_url_name

        Name of the url to add another choice via a javascript popup. If empty
        then no "add another" link will appear.
    """
    choice_html_format = u'<span class="div" data-value="%s">%s</span>'
    empty_html_format = u'<span class="div"><em>%s</em></span>'
    autocomplete_html_format = u'%s'
    add_another_url_name = None

    def choices_for_request(self):
        """
        Return the list of choices that are available. Uses :py:attr:`request`
        if set, this method is used by
        :py:meth:`~.base.AutocompleteBase.autocomplete_html`.
        """
        raise NotImplemented()

    def validate_values(self):
        """
        This basic implementation returns True if all
        :py:attr:`~AutocompleteInterface.values` are in
        :py:meth:`~.base.AutocompleteInterface.choices_for_values`.
        """
        return len(self.choices_for_values()) == len(self.values)

    def autocomplete_html(self):
        """
        Simple rendering of the autocomplete.

        It will append the result of
        :py:meth:`~.base.AutocompleteBase.choice_html` for each choice returned
        by :py:meth:`~.base.AutocompleteBase.choices_for_request`, and
        wrap that in :py:attr:`autocomplete_html_format`.
        """
        html = []

        for choice in self.choices_for_request():
            html.append(self.choice_html(choice))

        if not html:
            html = self.empty_html_format % _('no matches found').capitalize()

        return self.autocomplete_html_format % ''.join(html)

    def choice_html(self, choice):
        """
        Format a choice using :py:attr:`choice_html_format`.
        """
        return self.choice_html_format % (
            escape(self.choice_value(choice)),
            escape(self.choice_label(choice)))

    def choice_value(self, choice):
        """
        Return the value of a choice. This simple implementation returns the
        textual representation.
        """
        return force_text(choice)

    def choice_label(self, choice):
        """
        Return the human-readable representation of a choice. This simple
        implementation returns the textual representation.
        """
        return force_text(choice)
