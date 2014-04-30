"""Admin classes for the aps_process app."""
from django.contrib import admin

from . import models


# ======
# Mixins
# ======

class DefaultProcessAdmin(admin.ModelAdmin):
    """Common defaults for all admins."""
    save_on_top = True
    exclude = ('source', 'lft', 'rght', 'lvl')


class DefaultProcessTabularInline(admin.TabularInline):
    exclude = ('source', 'lft', 'rght', 'lvl')


# =======
# Inlines
# =======

class CalendarBucketInline(DefaultProcessTabularInline):
    model = models.CalendarBucket
    extra = 0


class FlowInline(DefaultProcessTabularInline):
    model = models.Flow
    raw_id_fields = ('operation', 'thebuffer', )
    extra = 0


class ResourceLoadInline(DefaultProcessTabularInline):
    model = models.ResourceLoad
    raw_id_fields = ('operation', 'resource', )
    extra = 0


class SetupRuleInline(DefaultProcessTabularInline):
    model = models.SetupRule
    extra = 3
    exclude = ('source', )


class SubOperationInline(DefaultProcessTabularInline):
    model = models.SubOperation
    fk_name = 'operation'
    extra = 1
    raw_id_fields = ('suboperation', )


# ===========
# ModelAdmins
# ===========

class BufferAdmin(DefaultProcessAdmin):
    """Custom admin for the ``Buffer`` model."""
    raw_id_fields = ('location', 'item', 'minimum_calendar', 'producing',
                     'owner', )
    list_display = (
        'name', 'description', 'category', 'subcategory', 'location', 'item',
        'onhand', 'minimum', 'minimum_calendar', 'producing', 'carrying_cost',
        'source', 'lastmodified')
    inlines = [FlowInline]


class CalendarAdmin(DefaultProcessAdmin):
    """Custom admin for the ``Calendar`` model."""
    list_display = (
        'name', 'description', 'category', 'subcategory', 'defaultvalue',
        'source', 'lastmodified')
    inlines = [CalendarBucketInline]


class CalendarBucketAdmin(DefaultProcessAdmin):
    """Custom admin for the ``CalendarBucket`` model."""
    raw_id_fields = ('calendar', )
    list_display = (
        'id', 'startdate', 'enddate', 'value', 'priority', 'monday', 'tuesday',
        'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'starttime',
        'endtime', 'source', 'lastmodified')


class FlowAdmin(DefaultProcessAdmin):
    """Custom admin for the ``Flow`` model."""
    raw_id_fields = ('operation', 'thebuffer',)
    list_display = (
        'id', 'operation', 'thebuffer', 'type', 'quantity', 'effective_start',
        'effective_end', 'name', 'alternate', 'priority', 'source',
        'lastmodified')


class ItemAdmin(DefaultProcessAdmin):
    """Custom admin for the ``Item`` model."""
    raw_id_fields = ('operation', 'owner',)
    list_display = (
        'name', 'description', 'category', 'subcategory', 'operation', 'price',
        'source', 'lastmodified')


class LocationAdmin(DefaultProcessAdmin):
    """Custom admin for the ``Location`` model."""
    raw_id_fields = ('available', 'owner',)
    list_display = (
        'name', 'description', 'category', 'subcategory', 'available',
        'source', 'lastmodified')


class OperationAdmin(DefaultProcessAdmin):
    """Custom admin for the ``Location`` model."""
    raw_id_fields = ('location',)
    list_display = (
        'name', 'type', 'description', 'category', 'subcategory', 'location',
        'setup', 'batchqty', 'batchtime', 'setup', 'setdown', 'source',
        'lastmodified')
    inlines = [SubOperationInline, FlowInline, ResourceLoadInline]


class ResourceAdmin(DefaultProcessAdmin):
    """Custom admin for the ``Resource`` model."""
    raw_id_fields = ('maximum_calendar', 'location', 'setupmatrix', 'owner')
    list_display = (
        'name', 'description', 'category', 'subcategory', 'maximum',
        'maximum_calendar', 'location', 'cost', 'maxearly', 'setupmatrix',
        'setup', 'source', 'lastmodified')
    inlines = [ResourceLoadInline]


class ResourceLoadAdmin(DefaultProcessAdmin):
    """Custom admin for the ``ResourceLoad`` model."""
    raw_id_fields = ('operation', 'resource')
    list_display = (
        'id', 'operation', 'resource', 'quantity', 'effective_start',
        'effective_end', 'name', 'alternate', 'priority', 'setup', 'search',
        'source', 'lastmodified')


class SetupMatrixAdmin(DefaultProcessAdmin):
    """Custom admin for the ``SetupMatrix`` model."""
    list_display = (
        'name', 'source', 'lastmodified')
    inlines = [SetupRuleInline]


class SubOperationAdmin(DefaultProcessAdmin):
    """Custom admin for the ``SubOperation`` model."""
    raw_id_fields = ('operation', 'suboperation',)
    list_display = (
        'id', 'operation', 'priority', 'suboperation', 'effective_start',
        'effective_end', 'source', 'lastmodified')


# ============
# Registration
# ============

admin.site.register(models.Buffer, BufferAdmin)
admin.site.register(models.Calendar, CalendarAdmin)
admin.site.register(models.CalendarBucket, CalendarBucketAdmin)
admin.site.register(models.Flow, FlowAdmin)
admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Operation, OperationAdmin)
admin.site.register(models.Resource, ResourceAdmin)
admin.site.register(models.ResourceLoad, ResourceLoadAdmin)
admin.site.register(models.SetupMatrix, SetupMatrixAdmin)
admin.site.register(models.SubOperation, SubOperationAdmin)
