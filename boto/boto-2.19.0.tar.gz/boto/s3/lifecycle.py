# Copyright (c) 2012 Mitch Garnaat http://garnaat.org/
# Copyright (c) 2012 Amazon.com, Inc. or its affiliates.  All Rights Reserved
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


class Rule(object):
    """
    A Lifcycle rule for an S3 bucket.

    :ivar id: Unique identifier for the rule. The value cannot be longer
        than 255 characters.

    :ivar prefix: Prefix identifying one or more objects to which the
        rule applies.

    :ivar status: If Enabled, the rule is currently being applied.
        If Disabled, the rule is not currently being applied.

    :ivar expiration: An instance of `Expiration`. This indicates
        the lifetime of the objects that are subject to the rule.

    :ivar transition: An instance of `Transition`.  This indicates
        when to transition to a different storage class.

    """
    def __init__(self, id=None, prefix=None, status=None, expiration=None,
                 transition=None):
        self.id = id
        self.prefix = prefix
        self.status = status
        if isinstance(expiration, (int, long)):
            # retain backwards compatibility???
            self.expiration = Expiration(days=expiration)
        else:
            # None or object
            self.expiration = expiration
        self.transition = transition

    def __repr__(self):
        return '<Rule: %s>' % self.id

    def startElement(self, name, attrs, connection):
        if name == 'Transition':
            self.transition = Transition()
            return self.transition
        elif name == 'Expiration':
            self.expiration = Expiration()
            return self.expiration
        return None

    def endElement(self, name, value, connection):
        if name == 'ID':
            self.id = value
        elif name == 'Prefix':
            self.prefix = value
        elif name == 'Status':
            self.status = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '<Rule>'
        s += '<ID>%s</ID>' % self.id
        s += '<Prefix>%s</Prefix>' % self.prefix
        s += '<Status>%s</Status>' % self.status
        if self.expiration is not None:
            s += self.expiration.to_xml()
        if self.transition is not None:
            s += self.transition.to_xml()
        s += '</Rule>'
        return s

class Expiration(object):
    """
    When an object will expire.

    :ivar days: The number of days until the object expires

    :ivar date: The date when the object will expire. Must be
        in ISO 8601 format.
    """
    def __init__(self, days=None, date=None):
        self.days = days
        self.date = date

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Days':
            self.days = int(value)
        elif name == 'Date':
            self.date = value

    def __repr__(self):
        if self.days is None:
            how_long = "on: %s" % self.date
        else:
            how_long = "in: %s days" % self.days
        return '<Expiration: %s>' % how_long

    def to_xml(self):
        s = '<Expiration>'
        if self.days is not None:
            s += '<Days>%s</Days>' % self.days
        elif self.date is not None:
            s += '<Date>%s</Date>' % self.date
        s += '</Expiration>'
        return s

class Transition(object):
    """
    A transition to a different storage class.

    :ivar days: The number of days until the object should be moved.

    :ivar date: The date when the object should be moved.  Should be
        in ISO 8601 format.

    :ivar storage_class: The storage class to transition to.  Valid
        values are GLACIER.

    """
    def __init__(self, days=None, date=None, storage_class=None):
        self.days = days
        self.date = date
        self.storage_class = storage_class

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Days':
            self.days = int(value)
        elif name == 'Date':
            self.date = value
        elif name == 'StorageClass':
            self.storage_class = value

    def __repr__(self):
        if self.days is None:
            how_long = "on: %s" % self.date
        else:
            how_long = "in: %s days" % self.days
        return '<Transition: %s, %s>' % (how_long, self.storage_class)

    def to_xml(self):
        s = '<Transition>'
        s += '<StorageClass>%s</StorageClass>' % self.storage_class
        if self.days is not None:
            s += '<Days>%s</Days>' % self.days
        elif self.date is not None:
            s += '<Date>%s</Date>' % self.date
        s += '</Transition>'
        return s

class Lifecycle(list):
    """
    A container for the rules associated with a Lifecycle configuration.
    """

    def startElement(self, name, attrs, connection):
        if name == 'Rule':
            rule = Rule()
            self.append(rule)
            return rule
        return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def to_xml(self):
        """
        Returns a string containing the XML version of the Lifecycle
        configuration as defined by S3.
        """
        s = '<?xml version="1.0" encoding="UTF-8"?>'
        s += '<LifecycleConfiguration>'
        for rule in self:
            s += rule.to_xml()
        s += '</LifecycleConfiguration>'
        return s

    def add_rule(self, id, prefix, status, expiration, transition=None):
        """
        Add a rule to this Lifecycle configuration.  This only adds
        the rule to the local copy.  To install the new rule(s) on
        the bucket, you need to pass this Lifecycle config object
        to the configure_lifecycle method of the Bucket object.

        :type id: str
        :param id: Unique identifier for the rule. The value cannot be longer
            than 255 characters.

        :type prefix: str
        :iparam prefix: Prefix identifying one or more objects to which the
            rule applies.

        :type status: str
        :param status: If 'Enabled', the rule is currently being applied.
            If 'Disabled', the rule is not currently being applied.

        :type expiration: int
        :param expiration: Indicates the lifetime, in days, of the objects
            that are subject to the rule. The value must be a non-zero
            positive integer. A Expiration object instance is also perfect.

        :type transition: Transition
        :param transition: Indicates when an object transitions to a
            different storage class. 
        """
        rule = Rule(id, prefix, status, expiration, transition)
        self.append(rule)
