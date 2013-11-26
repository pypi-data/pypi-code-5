import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.addons.careers.managers import CareerManager

POSITION_TYPE_CHOICES = (
                ('full time', _('Full Time')),
                ('part time', _('Part Time')),
                ('permanent', _('Permanent')),
                ('contract', _('Contract')),
                )


class Career(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    company = models.CharField(_('Company'), max_length=150)
    company_description = models.TextField(_('Company Description'),
                                           blank=True,
                                           default='')
    position_title = models.CharField(_('Position Title'),
                                      max_length=150)
    position_description = models.TextField(_('Position Description'),
                                           blank=True,
                                           default='')
    position_type = models.CharField(_('Position Type'),
                                      max_length=50,
                                      choices=POSITION_TYPE_CHOICES,
                                      default='full time')

    start_dt = models.DateTimeField(_('Start Date/Time'),
                                         null=True, blank=True)
    end_dt = models.DateTimeField(_('End Date/Time'),
                                         null=True, blank=True)
    experience = models.TextField(_('Experience'),
                                           blank=True,
                                           default='')
    user = models.ForeignKey(User, related_name="careers")

    perms = generic.GenericRelation(ObjectPermission,
                                  object_id_field="object_id",
                                  content_type_field="content_type")

    objects = CareerManager()

    class Meta:
        permissions = (("view_career", "Can view career"),)
        verbose_name = "Career"
        verbose_name_plural = "Careers"

    def __unicode__(self):
        return '%s - %s' % (self.company, self.user)

#    @models.permalink
#    def get_absolute_url(self):
#        return ("career", [self.pk])

    def save(self, *args, **kwargs):
        self.guid = self.guid or unicode(uuid.uuid1())

        super(Career, self).save(*args, **kwargs)
