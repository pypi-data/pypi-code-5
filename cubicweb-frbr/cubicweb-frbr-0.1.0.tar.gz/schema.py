# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-frbr schema"""

# See http://archive.ifla.org/VII/s13/frbr/frbr2.htm

from yams.buildobjs import (EntityType, RelationDefinition, SubjectRelation, Boolean, Float,
                            String, Int, BigInt, Date)
from yams.constraints import SizeConstraint
from cubicweb.schemas.base import ExternalUri

addr_constraints = ExternalUri.get_relation('uri').constraints
for cstr in addr_constraints[:]:
    if isinstance(cstr, SizeConstraint):
        addr_constraints.remove(cstr)
        break


class _AbstractEntity(EntityType):
    __abstract__ = True
    title = String(required=True, indexed=True, fulltextindexed=True)
    frbnf = Int(indexed=True)
    preferred_label =SubjectRelation('Name', cardinality='1?', inlined=True)
    alt_labels =SubjectRelation('Name', cardinality='**')
    deweys =SubjectRelation('Dewey', cardinality='**')
    description = String(fulltextindexed=True)
    id = Int(indexed=True) # Other possible ids, e.g. mb_id
    type = String(maxsize=256, indexed=True) # E.g. for corporate bodies, places, ...


### WORK ELEMENTS
class Work(_AbstractEntity):
    start_date = Date()
    stop_date = Date()
    musical_genre = SubjectRelation('ExternalUri', cardinality='**')
    nationality = SubjectRelation('Country', cardinality='?*')
    languages = SubjectRelation('Language', cardinality='**')


class Expression(EntityType):
    pass


class Manifestation(EntityType):
    title = String(maxsize=2048, indexed=True, fulltextindexed=True)
    ean = String(maxsize=256, indexed=True)
    ismn = String(maxsize=256, indexed=True)
    isbn = String(maxsize=256, indexed=True)
    frbnf = Int(indexed=True)
    formatted_isbn = BigInt(indexed=True)
    dcmitype = String(maxsize=64, indexed=True)
    edition_date = Date()
    edition = String()
    publisher = String()
    publication = String()
    publication_place = String()
    description = String(fulltextindexed=True)
    languages = SubjectRelation('Language', cardinality='**')
    deweys =SubjectRelation('Dewey', cardinality='**')
    numerized_editions = SubjectRelation('ExternalUri', cardinality='*?')
    publication_location = SubjectRelation('Place', cardinality='?*', inlined=True)



class Item(EntityType):
    number = BigInt(indexed=True)
    cote = String(maxsize=64)
    section = String(maxsize=64)
    location = SubjectRelation('Place', cardinality='?*', inlined=True)


### CONTRIBUTION ELEMENTS
class Contribution(EntityType):
    # TODO: Not inlined for now as inlined relation conversion is
    # not possible in the current MassiveObjectStore
    manifestation = SubjectRelation(('Expression', 'Manifestation'), cardinality='1*')
    contributor = SubjectRelation(('Agent', 'Person', 'CorporateBody', 'Family'), cardinality='1*')
    role = SubjectRelation('Role', inlined=True, cardinality='1*')


class WorkManifested(EntityType):
    # TODO: Not inlined for now as inlined relation conversion is
    # not possible in the current MassiveObjectStore
    manifestation = SubjectRelation(('Expression', 'Manifestation'), cardinality='1*')
    work = SubjectRelation('Work', cardinality='1*')
    auto_create = Boolean(default=False)


class SubjectManifested(EntityType):
    # TODO: Not inlined for now as inlined relation conversion is
    # not possible in the current MassiveObjectStore
    manifestation = SubjectRelation(('Expression', 'Manifestation'), cardinality='1*')
    subject = SubjectRelation(('Subject', 'Concept', 'Place', 'Event', 'Object',
                               'Work', 'Agent', 'Person', 'CorporateBody', 'Family'),
                              cardinality='1*')
    auto_create = Boolean(default=False)


### AUTHORITIES ELEMENTS
class Agent(_AbstractEntity):
    """ http://rdvocab.info/uri/schema/FRBRentitiesRDA/Agent """
    ipi = String(maxsize=256, indexed=True)
    isni = String(maxsize=256, indexed=True)
    nationality = SubjectRelation('Country', cardinality='?*')
    languages = SubjectRelation('Language', cardinality='**')


class Person(Agent):
    """ http://rdvocab.info/uri/schema/FRBRentitiesRDA/Person"""
    given_name = String(maxsize=256, indexed=True, fulltextindexed=True)
    family_name = String(maxsize=256, indexed=True, fulltextindexed=True)
    dates = String(maxsize=256, indexed=True, fulltextindexed=True)
    gender = String(vocabulary=(_('male'), _('female')))
    birthdate = Date()
    deathdate = Date()
    # Link to Place ?
    birthplace = String(maxsize=256, indexed=True, fulltextindexed=True)
    deathplace = String(maxsize=256, indexed=True, fulltextindexed=True)
    birth_location = SubjectRelation('Place', cardinality='?*', inlined=True)
    death_location = SubjectRelation('Place', cardinality='?*', inlined=True)


class CorporateBody(Agent):
    start_date = Date()
    stop_date = Date()
    activity_start = Date()
    activity_stop = Date()
    # Link to Place ?
    start_place = String(maxsize=256, indexed=True, fulltextindexed=True)
    stop_place = String(maxsize=256, indexed=True, fulltextindexed=True)
    start_location = SubjectRelation('Place', cardinality='?*', inlined=True)
    stop_location = SubjectRelation('Place', cardinality='?*', inlined=True)


class Family(Agent):
    family_name = String(maxsize=256, indexed=True, fulltextindexed=True)
    start_location = SubjectRelation('Place', cardinality='?*', inlined=True)
    stop_location = SubjectRelation('Place', cardinality='?*', inlined=True)


### SUBJECT ELEMENTS
class Subject(_AbstractEntity):
    pass


class Concept(Subject):
    pass


class Place(Subject):
    latitude = Float(required=True)
    longitude = Float(required=True)
    country = SubjectRelation('Country', cardinality='?*', inlined=True)


class Event(Subject):
    start_date = Date()
    end_date = Date()


class Object(Subject):
    pass


### SECONDARY ELEMENTS
class Name(EntityType):
    title = String(indexed=True, fulltextindexed=True)
    id = Int(indexed=True) # Other possible ids, e.g. mb_id
    type = String(maxsize=256, indexed=True)
    start_date = Date()
    stop_date = Date()
    additional_infos = String(maxsize=1024, indexed=True, fulltextindexed=True)


### VOCABULARIES
class _AbstractVocabulary(EntityType):
    __abstract__ = True
    name = String(maxsize=256, internationalizable=True)
    code = String(unique=True, maxsize=10)
    frequency = Int(indexed=True)
    sort_key = Int(unique=True, indexed=True)
    id = Int(indexed=True) # Other possible ids, e.g. mb_id


class Country(_AbstractVocabulary):
    altlabels = String(maxsize=512) # joined with '###'


class Language(_AbstractVocabulary):
    code2 = String(maxsize=3, description='alternative code (XXX)')
    code3 = String(maxsize=2, description='2-letters code')


class Script(_AbstractVocabulary):
    iso_number = Int(indexed=True)
    language = SubjectRelation('Language', cardinality='?*', inlined=True)


class Dewey(_AbstractVocabulary):
    pass


class Role(_AbstractVocabulary):
    idloc = String(maxsize=64, indexed=True)


### RELATIONS
class realized_through(RelationDefinition):
    subject = 'Work'
    object = 'Expression'
    cardinality = '**'

class embodied_in(RelationDefinition):
    subject = 'Expression'
    object = 'Manifestation'
    cardinality = '**'

class exemplified_by(RelationDefinition):
    subject = 'Manifestation'
    object = 'Item'
    cardinality = '**'

class main_author(RelationDefinition):
    subject = 'Work'
    object = ('Agent', 'Person', 'CorporateBody', 'Family')
    cardinality = '**'

class close_match(RelationDefinition):
    subject = '*'
    object = 'ExternalUri'
    cardinality = '**'

class exact_match(RelationDefinition):
    subject = '*'
    object = 'ExternalUri'
    cardinality = '**'

class same_as(RelationDefinition):
    subject = '*'
    object = 'ExternalUri'
    cardinality = '**'

class see_also(RelationDefinition):
    subject = '*'
    object = 'ExternalUri'
    cardinality = '**'

class depictions(RelationDefinition):
    subject = '*'
    object = 'ExternalUri'
    cardinality = '**'

class related_concept(RelationDefinition):
    subject = 'Concept'
    object = 'Concept'
    cardinality = '**'

class broader_concept(RelationDefinition):
    subject = 'Concept'
    object = 'Concept'
    cardinality = '**'

class aggregated_by(RelationDefinition):
    subject = 'Work'
    object = 'Work'
    cardinality = '?*'

# Shortcut
class work_manifested(RelationDefinition):
    subject = 'Manifestation'
    object = 'Work'
    cardinality = '**'

class contributors(RelationDefinition):
    subject = 'Manifestation'
    object = ('Agent', 'Person', 'CorporateBody', 'Family')
    cardinality = '**'

class subject_manifested(RelationDefinition):
    subject = 'Manifestation'
    object = ('Subject', 'Concept', 'Place', 'Event', 'Object',
              'Work', 'Agent', 'Person', 'CorporateBody', 'Family')
    cardinality = '**'
