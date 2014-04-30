# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2013 CEA (Saclay, FRANCE), all rights reserved.
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

""" Registration and security tools
"""
from logilab.common.decorators import monkeypatch

from yams.schema import role_name

from cubicweb.server import repository
from cubicweb.server.ssplanner import EditedEntity
from cubicweb import ValidationError


###############################################################################
### REGISTRATION ##############################################################
###############################################################################
@monkeypatch(repository.Repository)
def register_user(self, login, password, email=None, **kwargs):
    with self.internal_session() as session:
        # for consistency, keep same error as unique check hook (although not required)
        errmsg = session._('the value "%s" is already used, use another one')
        if (session.execute('CWUser X WHERE X login %(login)s', {'login': login},
                            build_descr=False)
            or session.execute('CWUser X WHERE X use_email C, C address %(login)s',
                               {'login': login}, build_descr=False)):
            qname = role_name('login', 'subject')
            raise ValidationError(None, {qname: errmsg % login})
        # we have to create the user
        user = self.vreg['etypes'].etype_class('CWUser')(session)
        if isinstance(password, unicode):
            # password should *always* be utf8 encoded
            password = password.encode('UTF8')
        kwargs['login'] = login
        kwargs['upassword'] = password
        self.glob_add_entity(session, EditedEntity(user, **kwargs))
        ###################################
        # Monkeypatch register user to create the user in the "guests" group
        # for security reason (just read ability)
        session.execute('SET X in_group G WHERE X eid %(x)s, G name "guests"',
                        {'x': user.eid})
        ###################################
        if email or '@' in login:
            d = {'login': login, 'email': email or login}
            if session.execute('EmailAddress X WHERE X address %(email)s', d,
                               build_descr=False):
                qname = role_name('address', 'subject')
                raise ValidationError(None, {qname: errmsg % d['email']})
            session.execute('INSERT EmailAddress X: X address %(email)s, '
                            'U primary_email X, U use_email X '
                            'WHERE U login %(login)s', d, build_descr=False)
        session.commit()
    return True
