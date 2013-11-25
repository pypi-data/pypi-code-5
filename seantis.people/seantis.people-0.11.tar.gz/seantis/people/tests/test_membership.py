from datetime import date
from plone import api
from plone.uuid.interfaces import IUUID
from zope.interface import Invalid

from seantis.people.interfaces import IMembership, IPerson
from seantis.people.content import Membership
from seantis.people import tests


class TestMembership(tests.IntegrationTestCase):

    def test_membership_creation(self):
        with self.user('admin'):
            ms = api.content.create(
                id='test',
                type='seantis.people.membership',
                container=self.new_temporary_folder()
            )

        self.assertIs(type(ms.aq_base), Membership)

    def test_membership_range_validation(self):
        with self.user('admin'):
            ms = api.content.create(
                id='test',
                type='seantis.people.membership',
                container=self.new_temporary_folder()
            )

        ms.start, ms.end = None, None
        IMembership.validateInvariants(ms)

        ms.start, ms.end = date(2012, 1, 1), None
        IMembership.validateInvariants(ms)

        ms.start, ms.end = None, date(2012, 1, 1)
        IMembership.validateInvariants(ms)

        ms.start, ms.end = date(2012, 1, 1), date(2012, 1, 2)
        IMembership.validateInvariants(ms)

        ms.start, ms.end = date(2012, 1, 1), date(2012, 1, 1)
        IMembership.validateInvariants(ms)

        ms.start, ms.end = date(2012, 1, 2), date(2012, 1, 1)
        self.assertRaises(Invalid, IMembership.validateInvariants, ms)

    def test_membership_person_relation(self):
        person_type = self.new_temporary_type(
            behaviors=[IPerson.__identifier__]
        )

        with self.user('admin'):
            organization = self.new_temporary_folder('S.H.I.E.L.D')

            nick_fury = api.content.create(
                title='Nick Fury',
                type=person_type.id,
                container=self.new_temporary_folder()
            )

            tony_stark = api.content.create(
                title='Tony Stark',
                type=person_type.id,
                container=self.new_temporary_folder()
            )

            api.content.create(
                title='Director',
                type='seantis.people.membership',
                container=organization,
                person=nick_fury
            )

            api.content.create(
                title='Head',
                type='seantis.people.membership',
                container=organization,
                person=tony_stark
            )

        memberships = IPerson(nick_fury).memberships()

        org = IUUID(organization)

        self.assertEqual(len(memberships), 1)
        self.assertEqual(memberships.keys(), [org])
        self.assertEqual(len(memberships[org]), 1)
        self.assertEqual(memberships[org][0].Title, 'Director')

        with self.user('admin'):
            api.content.create(
                title='Leutenant',
                type='seantis.people.membership',
                container=organization,
                person=nick_fury
            )

        memberships = IPerson(nick_fury).memberships()

        self.assertEqual(len(memberships), 1)
        self.assertEqual(memberships.keys(), [org])
        self.assertEqual(len(memberships[org]), 2)
        self.assertEqual(memberships[org][0].Title, 'Director')
        self.assertEqual(memberships[org][1].Title, 'Leutenant')
