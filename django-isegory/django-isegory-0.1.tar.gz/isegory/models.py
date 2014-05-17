# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

import datetime


class Power(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def has_data(self):
        triads = self.triad_set.all()
        for item in triads:
            if item.data_set.count() > 0:
                return True


class Triad(models.Model):
    TRIAD_CHOICES = (
        (u"per", u"Personas"),
        (u"org", u"Organos"),
        (u"inf", u"Información"))
    name = models.CharField(max_length=3, choices=TRIAD_CHOICES)
    power = models.ForeignKey('Power')

    class Meta:
        ordering = ['power', '-name']

    def __unicode__(self):
        return "%s: %s" % (self.power.name, self.get_name_display())

    def has_data(self):
        if self.data_set.count() > 0:
            return True


class Data(models.Model):
    triad = models.ForeignKey('Triad')
    name = models.CharField(max_length=200)
    description = models.TextField()
    url_result_file = models.URLField()
    url_ckan = models.URLField(blank=True)
    updated = models.DateTimeField(_('date updated'),
                                   default=datetime.datetime.now())
    slug = models.SlugField(max_length=200)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Source(models.Model):
    data = models.ForeignKey('Data')
    name = models.CharField(max_length=200)
    description = models.TextField()
    howto_process = models.TextField(blank=True)
    manual = models.BooleanField(default=True)  # If manual source proccessing
    url_source = models.URLField(blank=True)
    url_script = models.URLField(blank=True)
    updated = models.DateTimeField(_('date updated'),
                                   default=datetime.datetime.now())

    def __unicode__(self):
        return self.name
