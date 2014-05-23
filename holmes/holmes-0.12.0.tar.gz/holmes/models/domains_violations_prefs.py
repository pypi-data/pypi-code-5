#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlalchemy as sa

from holmes.models import Base, JsonType
from holmes.models import Key, Domain


class DomainsViolationsPrefs(Base):
    __tablename__ = 'domains_violations_prefs'

    id = sa.Column(sa.Integer, primary_key=True)
    domain_id = sa.Column('domain_id', sa.Integer, sa.ForeignKey('domains.id'))
    key_id = sa.Column('key_id', sa.Integer, sa.ForeignKey('keys.id'))
    value = sa.Column('value', JsonType, nullable=True)

    def __str__(self):
        return '%s: %s' % (self.domain.name, self.key.name)

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            'domain': self.domain.name,
            'key': self.key.name,
            'value': self.value
        }

    @classmethod
    def get_domain_violation_prefs(cls, db):
        data = db.query(DomainsViolationsPrefs).all()

        import pdb; pdb.set_trace()

        prefs = {}
        for d in data:
            prefs[d.domain.name].append({
                'keyId': d.key.id,
                'keyName': d.key.name,
                'value': d.value
            })

        return prefs
