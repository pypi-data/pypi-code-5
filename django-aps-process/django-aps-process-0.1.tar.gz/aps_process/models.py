"""Models of the APS Process module."""
from datetime import datetime, time
from decimal import Decimal

from django.db import models
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _


# TODO General note: attributes in docstrings, where it was not entirely clear,
# what they refer to are marked with TODO for further update.


# ==========
# BaseModels
# ==========

class DateAndSource(models.Model):
    """
    Allows change dates and source of an object.

    :lastmodified: The date this object was modified the last time.
    :source: The source, that supplied the db entry.

    """
    source = models.CharField(verbose_name=_('Source'), max_length=20,
                              blank=True)
    lastmodified = models.DateTimeField(verbose_name=_('Lastmodified'),
                                        auto_now=True)

    class Meta:
        abstract = True


class Hierarchy(models.Model):
    """
    Base model, that adds everything to place the object in a certain level
    of the production process.

    :lft: TODO int
    :rght: TODO int
    :lvl: TODO int
    :name: Name of the item. Primary key!
    :owner: A parent object.

    """
    lft = models.IntegerField(verbose_name=_('Lft'), blank=True, null=True)
    rght = models.IntegerField(verbose_name=_('Rght'), blank=True, null=True)
    lvl = models.IntegerField(verbose_name=_('Lvl'), blank=True, null=True)
    name = models.CharField(verbose_name=_('Unique name'), max_length=60,
                            primary_key=True)
    owner = models.ForeignKey('self', verbose_name=_('Owner'),
                              blank=True, null=True, related_name='xchildren')

    class Meta:
        abstract = True


# ======
# Models
# ======

class Buffer(DateAndSource, Hierarchy):
    """
    :description: A description of the Buffer.
    :category: A string allowing categorization.
    :subcategory: A string allowing further sub-categorization.
    :type: The type of buffer. choices are:
      * default: filled by a production operation.
      * procure: filled by a supplier.
      * infinite: infinite supply.
    :location: FK to a Location where this buffer exists.
    :item: What Items are in this Buffer.
    :onhand: Inventory at the start of the planning period.
    :minimum: Minimum safety stock for this Buffer.
    :minimum_calendar: FK to the calendar, that holds minimum safety stock
      values.
    :producing: FK to the Operation, that fills the buffer.
    :carrying_cost: The cost of carrying inventory to this buffer
    :leadtime: The time between order and delivery of a material from a
      supplier.
    :fence: TODO also sth about ordering?
    :min_inventory: The minimum inventory, at which the stock should be filled
      up again.
    :max_inventory: The stock level that should be tried to reach with the
      refilling operation.
    :min_interval: The minimum interval between replenishing the Buffer.
    :max_interval: The maximum interval between replenishing the Buffer.
    :size_minimum: Minimum quantity for replenishment.
    :size_multiple: All replenishment actions are rounded up to a multiple of
      this value.
    :size_maximum: The maximum quantity for replenishment.

    """
    TYPE_CHOICES = (
        ('default', _('Default')),
        ('procure', _('Procure')),
        ('infinite', _('Infinite')),
    )

    description = models.CharField(verbose_name=_('Description'),
                                   max_length=200, blank=True)
    category = models.CharField(verbose_name=_('Category'), max_length=20,
                                blank=True)
    subcategory = models.CharField(verbose_name=_('Subcategory'),
                                   max_length=20, blank=True)
    type = models.CharField(verbose_name=_('Type'), max_length=20,
                            choices=TYPE_CHOICES, default='default',
                            blank=True)
    location = models.ForeignKey('aps_process.Location',
                                 verbose_name=_('Location'), blank=True,
                                 null=True, related_name='buffers')
    item = models.ForeignKey('aps_process.Item', verbose_name=_('Item'),
                             related_name='buffers')
    onhand = models.DecimalField(verbose_name=_('Onhand'), max_digits=15,
                                 decimal_places=4, default=Decimal('0.0'),
                                 blank=True, null=True)
    minimum = models.DecimalField(verbose_name=_('Minimum'), max_digits=15,
                                  decimal_places=4, default=Decimal('0.0'),
                                  blank=True, null=True)
    minimum_calendar = models.ForeignKey('aps_process.Calendar',
                                         verbose_name=_('Minimum calendar'),
                                         blank=True, null=True,
                                         related_name='buffers')
    producing = models.ForeignKey('aps_process.Operation',
                                  verbose_name=_('Producing'), blank=True,
                                  null=True, related_name='buffers')
    carrying_cost = models.DecimalField(verbose_name=_('Carrying cost'),
                                        max_digits=15, decimal_places=4,
                                        blank=True, null=True)
    leadtime = models.DecimalField(verbose_name=_('Leadtime'), max_digits=15,
                                   decimal_places=4, blank=True, null=True)
    fence = models.DecimalField(verbose_name=_('Fence'), max_digits=15,
                                decimal_places=4, blank=True, null=True)
    min_inventory = models.DecimalField(verbose_name=_('Min inventory'),
                                        max_digits=15, decimal_places=4,
                                        blank=True, null=True)
    max_inventory = models.DecimalField(verbose_name=_('Max inventory'),
                                        max_digits=15, decimal_places=4,
                                        blank=True, null=True)
    size_minimum = models.DecimalField(verbose_name=_('Size minimum'),
                                       max_digits=15, decimal_places=4,
                                       blank=True, null=True)
    size_multiple = models.DecimalField(verbose_name=_('Size multiple'),
                                        max_digits=15, decimal_places=4,
                                        blank=True, null=True)
    size_maximum = models.DecimalField(verbose_name=_('Size maximum'),
                                       max_digits=15, decimal_places=4,
                                       blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Calendar(DateAndSource):
    """
    Holds certain constraints for certain time periods. Works in conjunction
    with CalendarBucket, which refers individual Calendars.

    :name: The unique name of this Calendar. Primary key!
    :description: A description of the Calendar.
    :category: A string allowing categorization.
    :subcategory: A string allowing further sub-categorization.
    :defaultvalue: A default value, if no additional bucket values apply.

    """
    name = models.CharField(verbose_name=_('Name'), max_length=60,
                            primary_key=True)
    description = models.CharField(verbose_name=_('Description'),
                                   max_length=200, blank=True)
    category = models.CharField(verbose_name=_('Category'), max_length=20,
                                blank=True)
    subcategory = models.CharField(verbose_name=_('Subcategory'),
                                   max_length=20, blank=True)
    defaultvalue = models.DecimalField(verbose_name=_('Default value'),
                                       max_digits=15, decimal_places=4,
                                       blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class CalendarBucket(DateAndSource):
    """
    Holds certain constraints, that apply to specific date ranges.

    :id: Primary key AutoField. Positive integer identifier.
    :calendar: The calendar, this bucket belongs to.
    :startdate: The start date and time of this bucket. TZ aware.
    :enddate: The date date and time of this bucket. TZ aware.
    :value: The value, that applies for these dates.
    :priority: The priority order of this SubOperation. Lower numbers indicate
      higher priority.
    :monday, tuesday, wednesday, thursday, friday, saturday, sunday: True, if
      the bucket applies to this day.
    :starttime: TODO time WITHOUT TZ awareness.
    :endtime: TODO time WITHOUT TZ awareness.

    """

    id = models.AutoField(_('identifier'), primary_key=True)
    calendar = models.ForeignKey(Calendar, verbose_name=_('Calendar'),
                                 related_name='buckets')
    startdate = models.DateTimeField(verbose_name=_('Start date'), blank=True,
                                     null=True)
    enddate = models.DateTimeField(verbose_name=_('End date'),
                                   default=datetime(2050, 12, 31).replace(
                                       tzinfo=utc),
                                   blank=True, null=True)
    value = models.DecimalField(verbose_name=_('Value'), max_digits=15,
                                decimal_places=4, default=Decimal('0.0'),
                                blank=True, null=True)
    priority = models.IntegerField(verbose_name=_('Priority'), default=1,
                                   blank=True, null=True)

    monday = models.BooleanField(verbose_name=_('Monday'), default=True)
    tuesday = models.BooleanField(verbose_name=_('Tuesday'), default=True)
    wednesday = models.BooleanField(verbose_name=_('Wednesday'), default=True)
    thursday = models.BooleanField(verbose_name=_('Thursday'), default=True)
    friday = models.BooleanField(verbose_name=_('Friday'), default=True)
    saturday = models.BooleanField(verbose_name=_('Saturday'), default=True)
    sunday = models.BooleanField(verbose_name=_('Sunday'), default=True)
    starttime = models.TimeField(verbose_name=_('Start time'),
                                 default=time(0, 0, 0), blank=True, null=True)
    endtime = models.TimeField(verbose_name=_('End time'),
                               default=time(23, 59, 59), blank=True, null=True)

    def __unicode__(self):
        return unicode(self.id)

    class Meta:
        ordering = ('calendar', 'id', )


class Flow(DateAndSource):
    """
    Abstraction for the increment or decrement of material stocks on Buffers.

    :id: Primary key AutoField. Positive integer identifier.
    :operation: FK to an Operation that creates or uses materials.
    :thebuffer: The Buffer, that the operation is used on.
    :quantity: The numerical representation of the amount of materials used.
    :type: The type of flow. choices are:
      * start: takes place at the start of an operation
      * end: takes place at the end of an operation
      * fixed_start: takes place at the start of an operation and is
        independent of the amount of operations.
      * fixed_end: takes place at the end of an operation and is independent
        of the amount of operations.
    :effective_start: TODO DateTime
    :effective_end: TODO DateTime
    :name: A string representation of this flow
    :alternate: TODO
    :priority: An integer representation for priority. Lower numbers mean
      higher priority. Defaults to 1.


    """
    FLOW_CHOICES = (
        ('start', _('Start')),
        ('end', _('End')),
        ('fixed_start', _('Fixed start')),
        ('fixed_end', _('Fixed end')),
    )

    id = models.AutoField(_('identifier'), primary_key=True)
    operation = models.ForeignKey('aps_process.Operation',
                                  verbose_name=_('Operation'),
                                  related_name='flows')
    thebuffer = models.ForeignKey(Buffer, verbose_name=_('Buffer'),
                                  related_name='flows')
    quantity = models.DecimalField(verbose_name=_('Quantity'), max_digits=15,
                                   decimal_places=4, default=Decimal('1.0'))
    type = models.CharField(verbose_name=_('Type'), max_length=20,
                            choices=FLOW_CHOICES, default='start')
    effective_start = models.DateTimeField(verbose_name=_('Effective start'),
                                           blank=True, null=True)
    effective_end = models.DateTimeField(verbose_name=_('Effective end'),
                                         blank=True, null=True)
    name = models.CharField(verbose_name=_('Name'), max_length=60,
                            blank=True, null=True)
    alternate = models.CharField(verbose_name=_('Alternate'), max_length=60,
                                 blank=True)
    priority = models.IntegerField(verbose_name=_('Priority'), default=1,
                                   blank=True, null=True)

    def __unicode__(self):
        return '{0} - {1}'.format(self.operation.name, self.thebufer.name)

    class Meta:
        ordering = ('name', )
        unique_together = (('operation', 'thebuffer'), )


class Item(DateAndSource, Hierarchy):
    """
    A type of item, that is processed, produced or handled in any way.

    :description: A description of the Item.
    :category: A string allowing categorization.
    :subcategory: A string allowing further sub-categorization.
    :operation: A related operation.
    :price: Cost of the Item.

    """
    description = models.CharField(verbose_name=_('Description'),
                                   max_length=200, blank=True)
    category = models.CharField(verbose_name=_('Category'), max_length=20,
                                blank=True)
    subcategory = models.CharField(verbose_name=_('Subcategory'),
                                   max_length=20, blank=True)
    operation = models.ForeignKey('aps_process.Operation',
                                  verbose_name=_('Operation'),
                                  blank=True, null=True, related_name='items')
    price = models.DecimalField(verbose_name=_('Price'), max_digits=15,
                                decimal_places=4, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Location(DateAndSource, Hierarchy):
    """
    Represents a location within the production chain.

    :description: A description of the location.
    :category: A string allowing categorization.
    :subcategory: A string allowing further sub-categorization.
    :available: The calendar, that defines, this location's availability.
      E.g. some sites might be closed on weekends or holidays.

    """
    description = models.CharField(verbose_name=_('Description'),
                                   max_length=200, blank=True)
    category = models.CharField(verbose_name=_('Category'), max_length=20,
                                blank=True)
    subcategory = models.CharField(verbose_name=_('Subcategory'),
                                   max_length=20, blank=True)
    available = models.ForeignKey(Calendar, verbose_name=_('Available'),
                                  blank=True, null=True,
                                  related_name='locations')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Operation(DateAndSource):
    """
    An operation during the production process. e.g. "packaging" or "weaving".

    :name: The unique name of this Calendar. Primary key!
    :type: The type of Operation. Choices are:
      * fixed_time: The operation time does not depend on quantity. (Default)
      * time_per: The operation time increases with quantity.
      * alternate: A choice between different operations.
      * routing: TODO sub-operation dependant sequence?
      TODO NOTE: For alternate and routing, the SubOperations come into play.
    :description: A description of the Calendar.
    :category: A string allowing categorization.
    :subcategory: A string allowing further sub-categorization.
    :location: The location of the operation.
    :setup: TODO Decimal
    :batchqty: The size of a batch.
    :batchtime: TODO The time it needs to make a batch?
    :setdown: TODO Decimal

    """
    TYPE_CHOICES = (
        ('fixed_time', _('Fixed time')),
        ('time_per', _('Time per')),
        ('alternate', _('Alternate')),
        ('routing', _('Routing')),
    )

    name = models.CharField(verbose_name=_('Name'), max_length=60,
                            primary_key=True)
    type = models.CharField(verbose_name=_('Type'), max_length=20,
                            choices=TYPE_CHOICES, default='fixed_time',
                            blank=True)
    description = models.CharField(verbose_name=_('Description'),
                                   max_length=200, blank=True)
    category = models.CharField(verbose_name=_('Category'), max_length=20,
                                blank=True)
    subcategory = models.CharField(verbose_name=_('Subcategory'),
                                   max_length=20, blank=True)
    location = models.ForeignKey(Location, verbose_name=_('Location'),
                                 blank=True, null=True,
                                 related_name='operations')
    setup = models.DecimalField(verbose_name=_('SetUp'), max_digits=15,
                                decimal_places=4, blank=True, null=True)
    batchqty = models.IntegerField(verbose_name=_('BatchQTY'), default=1,
                                   blank=True, null=True)
    batchtime = models.DecimalField(verbose_name=_('Batchtime'), max_digits=15,
                                    decimal_places=4, default=Decimal('1.0'),
                                    blank=True, null=True)
    setdown = models.DecimalField(verbose_name=_('SetDown'), max_digits=15,
                                  decimal_places=4, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Resource(DateAndSource, Hierarchy):
    """
    Represents a resource in the production chain.


    :description: A description of the Resource.
    :category: A string allowing categorization.
    :subcategory: A string allowing further sub-categorization.
    :maximum: The maximum size of the resource
    :maximum_calendar: A calendar holding the maximums over time.
    :location: The location of the resource.
    :cost: The cost of the resource.
    :maxearly: TODO
    :setupmatrix: TODO
    :setup: TODO

    """
    description = models.CharField(verbose_name=_('Description'),
                                   max_length=200, blank=True)
    category = models.CharField(verbose_name=_('Category'), max_length=20,
                                blank=True)
    subcategory = models.CharField(verbose_name=_('Subcategory'),
                                   max_length=20, blank=True)
    maximum = models.DecimalField(verbose_name=_('Maximum'), max_digits=15,
                                  decimal_places=4, default=Decimal('1.0'),
                                  blank=True, null=True)
    maximum_calendar = models.ForeignKey(Calendar,
                                         verbose_name=_('Maximum calendar'),
                                         blank=True, null=True,
                                         related_name='resources')
    location = models.ForeignKey(Location, verbose_name=_('Location'),
                                 blank=True, null=True,
                                 related_name='resources')
    cost = models.DecimalField(verbose_name=_('Cost'), max_digits=15,
                               decimal_places=4, blank=True, null=True)
    maxearly = models.DecimalField(verbose_name=_('Maxearly'), max_digits=15,
                                   decimal_places=4, blank=True, null=True)
    setupmatrix = models.ForeignKey('aps_process.SetupMatrix',
                                    verbose_name=_('Setupmatrix'),
                                    blank=True, null=True,
                                    related_name='resources')
    setup = models.CharField(verbose_name=_('Setup'), max_length=60,
                             blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class ResourceLoad(DateAndSource):
    """
    Outlines the use of a resource.

    :id: Primary key AutoField. Positive integer identifier.
    :operation: A related operation.
    :resource: A related resource, that is used.
    :quantity: The amount of resource used.
    :effective_start: TODO DateTime
    :effective_end: TODO DateTime
    :name: A human readable name for this load.
    :alternate: TODO
    :priority: An integer representation for priority. Lower numbers mean
      higher priority. Defaults to 1.
    :setup: TODO
    :search: TODO

    """
    id = models.AutoField(_('identifier'), primary_key=True)
    operation = models.ForeignKey(Operation, verbose_name=_('Operation'),
                                  related_name='loads')
    resource = models.ForeignKey('aps_process.Resource',
                                 verbose_name=_('Resource'),
                                 related_name='loads')
    quantity = models.DecimalField(verbose_name=_('Quantity'), max_digits=15,
                                   decimal_places=4, default=Decimal('1.0'))
    effective_start = models.DateTimeField(verbose_name=_('Effective start'),
                                           blank=True, null=True)
    effective_end = models.DateTimeField(verbose_name=_('Effective end'),
                                         blank=True, null=True)
    name = models.CharField(verbose_name=_('Name'), max_length=60,
                            blank=True)
    alternate = models.CharField(verbose_name=_('Alternate'), max_length=60,
                                 blank=True)
    priority = models.IntegerField(verbose_name=_('Priority'), default=1,
                                   blank=True, null=True)
    setup = models.CharField(verbose_name=_('Setup'), max_length=60,
                             blank=True)
    search = models.CharField(verbose_name=_('Search'), max_length=20,
                              blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )
        unique_together = (('operation', 'resource'), )


class SetupMatrix(DateAndSource):
    """
    The master model, that the SetupRules belong to.

    :name: Name of the item. Primary key!

    """
    name = models.CharField(verbose_name=_('Name'), max_length=60,
                            primary_key=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class SetupRule(DateAndSource):
    """
    TODO

    :id: Primary key AutoField. Positive integer identifier.
    :setupmatrix: The SetupMatrix this rule belongs to.
    :priority: The priority order of this SubOperation. Lower numbers indicate
      higher priority.
    :fromsetup: TODO
    :tosetup: TODO
    :duration: TODO
    :cost: The cost of this rule.

    """
    id = models.AutoField(_('identifier'), primary_key=True)
    setupmatrix = models.ForeignKey(SetupMatrix, verbose_name=_('Setupmatrix'),
                                    related_name='rules')
    priority = models.IntegerField(verbose_name=_('Priority'), default=1)
    fromsetup = models.CharField(verbose_name=_('From setup'), max_length=60,
                                 blank=True)
    tosetup = models.CharField(verbose_name=_('To setup'), max_length=60,
                               blank=True)
    duration = models.DecimalField(verbose_name=_('Duration'), max_digits=15,
                                   decimal_places=0, blank=True, null=True)
    cost = models.DecimalField(verbose_name=_('Cost'), max_digits=15,
                               decimal_places=4, blank=True, null=True)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.setupmatrix.name, self.priority)

    class Meta:
        ordering = ('setupmatrix__name', 'priority', )
        unique_together = (('setupmatrix', 'priority'),)


class SubOperation(DateAndSource):
    """
    A more fine grained part of an Operation.

    :id: Primary key AutoField. Positive integer identifier.
    :operation: The Operation this SubOperation belongs to.
    :priority: The priority order of this SubOperation. Lower numbers indicate
      higher priority.
    :suboperation: TODO Parent SubOperation? But if so, why char 60?
    :effective_start: TODO DateTime
    :effective_end: TODO DateTime

    """
    id = models.AutoField(_('identifier'), primary_key=True)
    operation = models.ForeignKey(Operation, verbose_name=_('Operation'),
                                  related_name='suboperations')
    priority = models.IntegerField(verbose_name=_('Priority'), default=1)
    suboperation = models.ForeignKey(Operation, verbose_name=_('Suboperation'),
                                     related_name='superoperations')
    effective_start = models.DateTimeField(verbose_name=_('Effective start'),
                                           blank=True, null=True)
    effective_end = models.DateTimeField(verbose_name=_('Effective end'),
                                         blank=True, null=True)

    def __unicode__(self):
        return u'{0}   {1}   {0}'.format(self.operation.name, self.priority,
                                         self.suboperation.name)

    class Meta:
        ordering = ('operation__name', 'priority', )
