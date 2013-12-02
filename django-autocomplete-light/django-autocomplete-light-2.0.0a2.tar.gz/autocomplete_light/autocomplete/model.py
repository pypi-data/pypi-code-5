from __future__ import unicode_literals
import six

from django.utils.encoding import force_text
from django.db.models import Q

from ..settings import DEFAULT_SEARCH_FIELDS

__all__ = ('AutocompleteModel', )


class AutocompleteModel(object):
    """
    Autocomplete which considers choices as a queryset.

    .. py:attribute:: choices

        A queryset.

    .. py:attribute:: limit_choices

        Maximum number of choices to display.

    .. py:attribute:: search_fields

        Fields to search in, configurable like on
        :py:attr:`django:django.contrib.admin.ModelAdmin.search_fields`

    .. py:attribute:: split_words

        If True, AutocompleteModel splits the search query into words and
        returns all objects that contain each of the words, case insensitive,
        where each word must be in at least one of search_fields. This mimics
        the mechanism of django's
        :py:attr:`django:django.contrib.admin.ModelAdmin.search_fields`.

        If 'or', AutocompleteModel does the same but returns all objects that
        contain **any** of the words.

    .. py:attribute:: order_by

        If set, it will be used to order choices. It can be a single field name
        or an iterable (ie. list, tuple).
    """
    limit_choices = 20
    choices = None
    search_fields = DEFAULT_SEARCH_FIELDS
    split_words = False
    order_by = None

    def choice_value(self, choice):
        """
        Return the pk of the choice by default.
        """
        return choice.pk

    def choice_label(self, choice):
        """
        Return the textual representation of the choice by default.
        """
        return force_text(choice)

    def order_choices(self, choices):
        """
        Order choices using :py:attr:`order_by` option if it is set.
        """
        if self.order_by is None:
            return choices

        if isinstance(self.order_by, six.string_types):
            return choices.order_by(self.order_by)

        return choices.order_by(*self.order_by)

    def choices_for_values(self):
        """
        Return ordered choices which pk are in
        :py:attr:`~.base.AutocompleteInterface.values`.
        """
        assert self.choices is not None, 'choices should be a queryset'
        return self.order_choices(self.choices.filter(
            pk__in=self.values or []))

    def choices_for_request(self):
        """
        Return a queryset based on :py:attr:`choices` using options
        :py:attr:`split_words`, :py:attr:`search_fields` and
        :py:attr:`limit_choices`.
        """
        assert self.choices is not None, 'choices should be a queryset'
        assert self.search_fields, 'autocomplete.search_fields must be set'
        q = self.request.GET.get('q', '')
        exclude = self.request.GET.getlist('exclude')

        conditions = self._choices_for_request_conditions(q,
                self.search_fields)

        return self.order_choices(self.choices.filter(
            conditions).exclude(pk__in=exclude))[0:self.limit_choices]

    def _construct_search(self, field_name):
        """
        Using a field name optionnaly prefixed by `^`, `=`, `@`, return a
        case-insensitive filter condition name usable as a queryset `filter()`
        keyword argument.
        """
        if field_name.startswith('^'):
            return "%s__istartswith" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            return "%s__search" % field_name[1:]
        else:
            return "%s__icontains" % field_name

    def _choices_for_request_conditions(self, q, search_fields):
        """
        Return a `Q` object usable by `filter()` based on a list of fields to
        search in `search_fields` for string `q`.

        It uses options `split_words` and `search_fields` . Refer to the
        class-level documentation for documentation on each of these options.
        """
        conditions = Q()

        if self.split_words:
            for word in q.strip().split():
                word_conditions = Q()
                for search_field in search_fields:
                    word_conditions |= Q(**{
                        self._construct_search(search_field): word})

                if self.split_words == 'or':
                    conditions |= word_conditions
                else:
                    conditions &= word_conditions
        else:
            for search_field in search_fields:
                conditions |= Q(**{self._construct_search(search_field): q})

        return conditions

    def validate_values(self):
        """
        Return True if all values where found in :py:attr:`choices`.
        """
        return len(self.choices_for_values()) == len(self.values)
