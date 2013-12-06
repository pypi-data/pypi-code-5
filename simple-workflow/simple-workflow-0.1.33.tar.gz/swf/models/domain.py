# -*- coding: utf-8 -*-

# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from boto.swf.exceptions import SWFResponseError, SWFDomainAlreadyExistsError

from swf.constants import REGISTERED
from swf.models import BaseModel
from swf.models.base import ModelDiff
from swf.utils import immutable
from swf.exceptions import (AlreadyExistsError, DoesNotExistError,
                            ResponseError)


@immutable
class Domain(BaseModel):
    """Simple Workflow Domain wrapper

    :param      name: Name of the domain to register (unique)
    :type       name: string

    :param      retention_period: Domain's workflow executions records retention in days
    :type       retention_period: Integer

    :param      status: Specifies the registration status of the
                        workflow types to list. Valid values are:
                        * swf.constants.REGISTERED
                        * swf.constants.DEPRECATED
    :type       status: string

    :param      description: Textual description of the domain
    :type       description: string
    """

    __slots__ = [
        'name',
        'status',
        'description',
        'retention_period',
    ]

    def __init__(self, name,
                 status=REGISTERED,
                 description=None,
                 retention_period=30, *args, **kwargs):
        self.name = name
        self.status = status
        self.description = description
        self.retention_period = retention_period

        # immutable decorator rebinds class name,
        # so have to use generice self.__class__
        super(self.__class__, self).__init__(*args, **kwargs)

    def _diff(self):
        """Checks for differences between Domain instance
        and upstream version

        :returns: A list of swf.models.base.ModelDiff namedtuple describing
                  differences
        :rtype: list
        """
        try:
            description = self.connection.describe_domain(self.name)
        except SWFResponseError as e:
            if e.error_code == 'UnknownResourceFault':
                raise DoesNotExistError("Remote Domain does not exist")

            raise ResponseError(e.body['message'])

        domain_info = description['domainInfo']
        domain_config = description['configuration']

        return ModelDiff(
            ('name', self.name, domain_info['name']),
            ('status', self.status, domain_info['status']),
            ('description', self.description, domain_info.get('description')),
            ('retention_period', self.retention_period, domain_config['workflowExecutionRetentionPeriodInDays']),
        )

    @property
    def exists(self):
        """Checks if the Domain exists amazon-side

        :rtype: bool
        """
        try:
            self.connection.describe_domain(self.name)
        except SWFResponseError as e:
            if e.error_code == 'UnknownResourceFault':
                return False
            else:
                raise ResponseError(e.body['message'])

        return True

    def save(self):
        """Creates the domain amazon side"""
        try:
            self.connection.register_domain(self.name,
                                            str(self.retention_period),
                                            self.description)
        except SWFDomainAlreadyExistsError:
            raise AlreadyExistsError("Domain %s already exists amazon-side" % self.name)

    def delete(self):
        """Deprecates the domain amazon side"""
        try:
            self.connection.deprecate_domain(self.name)
        except SWFResponseError as e:
            if e.error_code == 'UnknownResourceFault':
                raise DoesNotExistError("Domain %s does not exist amazon-side" % self.name)

    def upstream(self):
        from swf.querysets.domain import DomainQuerySet
        qs = DomainQuerySet()
        return qs.get(self.name)

    def workflows(self, status=REGISTERED):
        """Lists the current domain's workflow types

        :param      status: Specifies the registration status of the
                            workflow types to list. Valid values are:
                            * swf.constants.REGISTERED
                            * swf.constants.DEPRECATED
        :type       status: string
        """
        from swf.querysets.workflow import WorkflowTypeQuerySet
        qs = WorkflowTypeQuerySet(self)
        return qs.all(registration_status=status)

    @property
    def executions(self):
        pass

    def __repr__(self):
        return '<{} name={} status={}>'.format(
               self.__class__.__name__, self.name, self.status)
