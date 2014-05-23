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
""" Conversion rules for RDF """
from datetime import datetime

from cubes.dataio import xy


# UTILITY FUNCTIONS
def normalize_uri(uri):
    return uri.split('#', 1)[0]


def _convert_date(_object):
    """ Convert an rdf value to a date
    """
    try:
        return datetime.strptime(_object, '%Y-%m-%d')
    except:
        date = '01-01-' + _object.replace('.', '0')
        try:
            return datetime.strptime(date, '%Y-%m-%d')
        except:
            return None


def _specific_etype_callback(rdf_properties, types):
    """ Correctly retrieve the Concept etype
    """
    if 'skos:prefLabel' in rdf_properties and 'owl:sameAs' in rdf_properties:
        for url, _type in rdf_properties['owl:sameAs']:
            # No type for Rameau, use link to Stitch
            if url.startswith('http://stitch.cs.vu.nl/vocabularies'):
                return 'Concept'
    if 'foaf:Person' in types:
        name = rdf_properties.get('skos:prefLabel')
        if name and '(famille)' in name[0][0]:
            return 'Family'
    elif not types and ('dc:contributor' in rdf_properties and
                        len([r for r in rdf_properties
                             if r.startswith('bnfroles')])):
        # At least one roles
        return 'Contribution'
    elif not types and 'rdarelationships:workManifested' in rdf_properties:
        # At least one roles
        return 'WorkManifested'
    elif not types and 'dc:subject' in rdf_properties:
        # At least one roles
        return 'SubjectManifested'


def _build_name_callback(name, rdf_properties):
    """ Build a Name entity
    """
    return 'Name', {'title': name}


def format_isbn(rdf_properties):
    if 'bnf-onto:isbn' in rdf_properties:
        isbn = rdf_properties['bnf-onto:isbn'][0]
        isbn = [i for i in isbn if i in '0123456789']
        return int(''.join(isbn)) if isbn else None


def format_contribution_cwuri(rdf_properties):
    author = normalize_uri(rdf_properties['dc:contributor'][0][0]).split('/')[-1]
    manif = normalize_uri(rdf_properties['rdf:about'][0][0]).split('/')[-1]
    role = [r for r in rdf_properties if r.startswith('bnfroles')][0]
    role = role.split(':')[-1]
    cwuri = u'http://data.bnf.fr/contribution/%s/%s/%s' % (author, manif, role)
    return cwuri


def format_workmanifested_cwuri(rdf_properties):
    manif = normalize_uri(rdf_properties['rdarelationships:workManifested'][0][0]).split('/')[-1]
    work = normalize_uri(rdf_properties['rdf:about'][0][0]).split('/')[-1]
    cwuri = u'http://data.bnf.fr/workmanifested/%s/%s' % (work, manif)
    return cwuri


def format_subjectmanifested_cwuri(rdf_properties):
    subject = normalize_uri(rdf_properties['dc:subject'][0][0]).split('/')[-1]
    manif = normalize_uri(rdf_properties['rdf:about'][0][0]).split('/')[-1]
    cwuri = u'http://data.bnf.fr/subjectmanifested/%s/%s' % (subject, manif)
    return cwuri


def format_contribution_manifestation(rel, predicate, rdf_properties):
    return normalize_uri(rdf_properties['rdf:about'][0][0])


def format_workmanifested_work(rel, predicate, rdf_properties):
    return normalize_uri(rdf_properties['rdarelationships:workManifested'][0][0])


def format_subjectmanifested_subject(rel, predicate, rdf_properties):
    return normalize_uri(rdf_properties['dc:subject'][0][0])


def format_contribution_role(rel, predicate, rdf_properties):
    code = predicate.split(':')[-1]
    return u'http://data.bnf.fr/vocabulary/roles/%s' % code


# INITIALISATION
xy.register_prefix('marcrel', 'http://id.loc.gov/vocabulary/relators/')
xy.register_prefix('bnfroles', 'http://data.bnf.fr/vocabulary/roles/')
xy.register_prefix('databnf', 'http://data.bnf.fr/ontologie/')
xy.register_prefix('bnf-onto', 'http://data.bnf.fr/ontology/bnf-onto/')
xy.register_prefix('ark', 'http://ark.bnf.fr/ark:/12148/')
xy.register_prefix('mo', 'http://musicontology.com/')
xy.register_prefix('ore', 'http://www.openarchives.org/ore/terms/')
xy.register_prefix('bio', 'http://vocab.org/bio/0.1/')

xy.set_base_uri(u'http://data.bnf.fr')
xy.set_uri_conversion_callback(normalize_uri)
xy.register_attribute_callback('Date', _convert_date)


# ETYPES
xy.add_equivalence('Manifestation', 'frbr:Manifestation')
xy.add_equivalence('Work', 'frbr:Work')
xy.add_equivalence('Person', 'foaf:Person')
xy.add_equivalence('CorporateBody', 'foaf:Organization')
xy.set_etype_callback(_specific_etype_callback)

xy.add_equivalence('* frbnf', 'bnf-onto:FRBNF')
xy.add_equivalence('* title', 'skos:prefLabel')
xy.add_equivalence('* title', 'rdfs:label')
xy.add_equivalence('* preferred_label Name', 'rdfs:label')
xy.add_equivalence('* preferred_label Name', 'skos:prefLabel')
xy.register_relations_etype_callbacks('preferred_label', _build_name_callback)
xy.add_equivalence('* alt_labels Name', 'skos:altLabel')
xy.register_relations_etype_callbacks('alt_labels', _build_name_callback)
xy.add_equivalence('* description', 'dc:description')
xy.add_equivalence('* description', 'skos:scopeNote')
xy.add_equivalence('* deweys Dewey', 'rdagroup2elements:fieldOfActivityOfThePerson')
xy.add_equivalence('* languages Language', 'rdagroup2elements:languageOfThePerson')
xy.add_equivalence('* nationality Country', 'rdagroup2elements:countryAssociatedWithThePerson')
xy.add_equivalence('* depictions ExternalUri', 'foaf:depiction')
xy.add_equivalence('* depictions ExternalUri', 'dbpediaowl:thumbnail')
xy.add_equivalence('* description', 'dbpediaowl:abstract')
xy.add_equivalence('* same_as ExternalUri', 'owl:sameAs')
xy.add_equivalence('* see_also ExternalUri', 'foaf:page')
xy.add_equivalence('* see_also ExternalUri', 'rdfs:seeAlso')
xy.add_equivalence('* see_also ExternalUri', 'foaf:isPrimaryTopicOf')
xy.add_equivalence('* close_match ExternalUri', 'skos:closeMatch')
xy.add_equivalence('* exact_match ExternalUri', 'skos:exactMatch')


xy.set_vocabulary('Country')
xy.set_vocabulary('Language')
xy.set_vocabulary('Script')
xy.set_vocabulary('Dewey')
xy.set_vocabulary('Role')


# AGENTS
xy.add_equivalence('Person given_name', 'foaf:givenName')
xy.add_equivalence('Person family_name', 'foaf:familyName')
xy.add_equivalence('Person dates', 'dc:date')
xy.add_equivalence('Person gender', 'foaf:gender')
xy.add_equivalence('Person birthplace', 'rdagroup2elements:placeOfBirth')
xy.add_equivalence('Person birthdate', 'bio:Birth')
xy.add_equivalence('Person deathplace', 'rdagroup2elements:placeOfDeath')
xy.add_equivalence('Person deathdate', 'bio:Death')

xy.add_equivalence('CorporateBody start_date', 'dc:date')
xy.add_equivalence('CorporateBody start_date', 'rdagroup2elements:dateAssociatedWithTheCorporateBody')
xy.add_equivalence('CorporateBody start_place', 'rdagroup2elements:placeAssociatedWithTheCorporateBody')
xy.add_equivalence('CorporateBody activity_date', 'rdagroup2elements:dateOfEstablishmet')
xy.add_equivalence('CorporateBody description', 'rdagroup2elements:corporateHistory')
xy.add_equivalence('CorporateBody deweys Dewey', 'rdagroup2elements:fieldOfActivityOfTheCorporateBody')


# WORK/EXPRESSION/MANIFESTATION
xy.add_equivalence('Work start_date', 'dc:date')
xy.add_equivalence('Work aggregated_by Work', 'ore:isAggregatedBy')
xy.add_equivalence('Work musical_genre ExternalUri', 'mo:genre')
xy.add_equivalence('Work main_author *', 'dc:creator')
xy.add_equivalence('Work main_author *', 'dc:creator')

xy.add_equivalence('Manifestation title', 'dc:title')
xy.register_attribute_callback('Manifestation formatted_isbn', format_isbn)
xy.add_equivalence('Manifestation isbn', 'bnf-onto:isbn')
xy.add_equivalence('Manifestation ean', 'bnf-onto:EAN')
xy.add_equivalence('Manifestation ismn', 'bnf-onto:ISMN')
xy.add_equivalence('Manifestation edition', 'rdagroup1elements:designationOfEdition')
xy.add_equivalence('Manifestation edition_date', 'dc:date')
xy.add_equivalence('Manifestation publisher', 'rdagroup1elements:publishersName')
xy.add_equivalence('Manifestation publication_place', 'rdagroup1elements:placeOfPublication')
xy.add_equivalence('Manifestation publication', 'dc:publisher')
xy.add_equivalence('Manifestation dcmitype', 'dc:type')
xy.add_equivalence('Manifestation numerized_editions ExternalUri', 'rdarelationships:electronicReproduction')
xy.add_equivalence('Manifestation languages Language', 'dc:language')


# SUBJECT/CONCEPT
xy.add_equivalence('Concept broader_concept Concept', 'skos:broader')
xy.add_equivalence('Concept related_concept Concept', 'skos:related')


# CONTRIBUTION AND OTHER ENTITY-RELATIONS
xy.register_attribute_callback('Contribution cwuri',
                               format_contribution_cwuri)
xy.add_equivalence('Contribution manifestation *', 'rdf:about')
xy.register_relation_callback('Contribution manifestation *',
                              format_contribution_manifestation)
xy.add_equivalence('Contribution contributor *', 'dc:contributor')
xy.add_equivalence('Contribution role Role', 'bnfroles:*')
xy.register_relation_callback('Contribution role Role',
                              format_contribution_role)

xy.register_attribute_callback('WorkManifested cwuri',
                               format_workmanifested_cwuri)
xy.add_equivalence('WorkManifested manifestation *', 'rdf:about')
xy.register_relation_callback('WorkManifested manifestation *',
                              format_contribution_manifestation)
xy.add_equivalence('WorkManifested work *', 'rdarelationships:workManifested')
xy.register_relation_callback('WorkManifested work *',
                              format_workmanifested_work)

xy.register_attribute_callback('SubjectManifested cwuri',
                               format_subjectmanifested_cwuri)
xy.add_equivalence('SubjectManifested manifestation *', 'rdf:about')
xy.register_relation_callback('SubjectManifested manifestation *',
                              format_contribution_manifestation)
xy.add_equivalence('SubjectManifested subject *', 'dc:subject')
xy.register_relation_callback('SubjectManifested subject *',
                              format_subjectmanifested_subject)
