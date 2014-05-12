import re
from django.utils.translation import ugettext_lazy as _
from django.forms import fields
from django.db import models
from django.db.models import ManyToManyField, Count, signals
from django.db.models.fields.related import add_lazy_relation

###################################################################################################
# MaxCardinalityManyToManyField from https://djangosnippets.org/snippets/2073/
#
# Limits the number of linked fields
class RelationCardinalityException(Exception):
    pass

class MaxCardinalityManyToManyField(ManyToManyField):
    '''A ManyToManyField that constrains the maximum number of relationships in
    one or both directions.

    An upper bound can be set for the forward relationships (``max_cardinality``)
    and/or the reverse relationships (``reverse_max_cardinality``). If either is
    left undefined (or None), it defaults to unbounded. Attempting to add one or
    more relationships that would result in exceeding the bound(s) raises a
    :class:`RelationCardinalityException`.

    For symmetric relationships, ``max_cardinality`` and ``reverse_max_cardinality``
    must be equal. As a shortcut, leaving one of the two undefined defaults to
    the other, so just defining one of them is enough.

    Example::

        class Topping(models.Model):
            name = models.CharField(max_length=128, unique=True)

        class Pizza(models.Model):
            name = models.CharField(max_length=128, unique=True)
            toppings = MaxCardinalityManyToManyField(Topping,
                                                     max_cardinality=2,
                                                     reverse_max_cardinality=3)

        >>> mushrooms = Topping.objects.get_or_create(name='mushrooms')[0]
        >>> anchovies = Topping.objects.get_or_create(name='anchovies')[0]
        >>> mozzarella = Topping.objects.get_or_create(name='mozzarella')[0]

        >>> margherita = Pizza.objects.get_or_create(name='margherita')[0]
        >>> marinara = Pizza.objects.get_or_create(name='marinara')[0]
        >>> sicilian = Pizza.objects.get_or_create(name='sicilian')[0]
        >>> california = Pizza.objects.get_or_create(name='california')[0]

        >>> # try to exceed max_cardinality through 'toppings'
        >>> margherita.toppings.add(mushrooms, anchovies)
        >>> margherita.toppings.add(mozzarella)
        Traceback (most recent call last):
        ...
        RelationCardinalityException: No more pizza-topping relationships allowed for pizza.pk=1
        >>> margherita.toppings.clear()

        >>> # try to exceed max_cardinality through 'pizza_set'
        >>> for topping in mushrooms, mozzarella:
        >>> ... topping.pizza_set = [marinara, sicilian]
        >>> anchovies.pizza_set.add(sicilian)
        Traceback (most recent call last):
        ...
        RelationCardinalityException: No more pizza-topping relationships allowed for pizza.pk=3
        >>> for topping in mushrooms, mozzarella, anchovies:
        >>> ... topping.pizza_set.clear()

        >>> # try to exceed reverse_max_cardinality through 'pizza_set'.
        >>> mushrooms.pizza_set.add(margherita, marinara, sicilian)
        >>> mushrooms.pizza_set.add(california)
        Traceback (most recent call last):
        ...
        RelationCardinalityException: No more pizza-topping relationships allowed for topping.pk=1
        >>> mushrooms.pizza_set.clear()

        >>> # try to exceed reverse_max_cardinality through 'toppings'
        >>> for pizza in margherita, marinara, sicilian:
        ...     pizza.toppings = [mushrooms, mozzarella]
        >>> california.toppings.add(mushrooms)
        RelationCardinalityException: No more pizza-topping relationships allowed for topping.pk=3
    '''

    def __init__(self, to, **kwargs):
        self.max_cardinality = kwargs.pop('max_cardinality', None)
        self.reverse_max_cardinality = kwargs.pop('reverse_max_cardinality', None)
        super(MaxCardinalityManyToManyField,self).__init__(to, **kwargs)
        if self.rel.symmetrical:
            if self.reverse_max_cardinality is None:
                self.reverse_max_cardinality = self.max_cardinality
            elif self.max_cardinality is None:
                self.max_cardinality = self.reverse_max_cardinality
            elif self.max_cardinality != self.reverse_max_cardinality:
                raise ValueError('Symmetrical relationships must have equal '
                                 'forward and reverse max cardinality')

    def contribute_to_class(self, cls, name):
        super(MaxCardinalityManyToManyField, self).contribute_to_class(cls, name)
        if self.max_cardinality or self.reverse_max_cardinality:
            through = self.rel.through
            if through:
                if isinstance(through, basestring):
                    add_lazy_relation(cls, self, through,
                        lambda self, through, cls: self.__connect_through_signals(through))
                else:
                    self.__connect_through_signals(through)

    def __connect_through_signals(self, through):

        def validate_cardinalities(sender, instance, **kwargs):
            pk = instance._get_pk_val()
            # XXX: _base_manager or _default_manager ?
            exists = pk is not None and instance.__class__._base_manager.filter(pk=pk).exists()
            if not exists:
                self._validate_cardinality(getattr(instance, self.m2m_column_name()),
                                           reverse=False)
                self._validate_cardinality(getattr(instance, self.m2m_reverse_name()),
                                           reverse=True)
        signals.pre_save.connect(validate_cardinalities, sender=through, weak=False)

        def m2m_validate_cardinalities(sender, instance, action, reverse, pk_set, **kwargs):
            if action != 'pre_add' or not pk_set:
                return
            if reverse:
                self._validate_cardinality(*pk_set, reverse=False)
                self._validate_cardinality(instance._get_pk_val(),
                                           reverse=True, num_added=len(pk_set))
            else:
                self._validate_cardinality(instance._get_pk_val(),
                                           reverse=False, num_added=len(pk_set))
                self._validate_cardinality(*pk_set, reverse=True)
        signals.m2m_changed.connect(m2m_validate_cardinalities, sender=through, weak=False)

    def _validate_cardinality(self, *pks, **kwargs):
        if not kwargs['reverse'] or self.rel.symmetrical:
            field_name = self.m2m_field_name()
            threshold = self.max_cardinality
        else:
            field_name = self.m2m_reverse_field_name()
            threshold = self.reverse_max_cardinality
        if threshold is None:
            return
        threshold -= kwargs.get('num_added', 1)
        for pk, count in self._get_counts(field_name, pks).iteritems():
            if count > threshold:
                raise RelationCardinalityException('No more %s allowed for %s.pk=%s' % (
                    unicode(self.rel.through._meta.verbose_name_plural), field_name, pk))

    def _get_counts(self, field_name, pks):
        pk2count = dict.fromkeys(pks, 0)  # ensure that all pks have a count
        pk2count.update(
            self.rel.through._default_manager.values_list(field_name).
            filter(**{field_name+'__in': pk2count}).annotate(Count(field_name)))
        return pk2count
