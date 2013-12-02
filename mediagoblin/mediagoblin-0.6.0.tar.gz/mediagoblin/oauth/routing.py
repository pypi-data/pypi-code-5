# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mediagoblin.tools.routing import add_route

# client registration & oauth
add_route(
        "mediagoblin.oauth",
        "/api/client/register",
        "mediagoblin.oauth.views:client_register"
        )

add_route(
        "mediagoblin.oauth",
        "/oauth/request_token",
        "mediagoblin.oauth.views:request_token"
        )

add_route(
        "mediagoblin.oauth",
        "/oauth/authorize",
        "mediagoblin.oauth.views:authorize",
        )

add_route(
        "mediagoblin.oauth",
        "/oauth/access_token",
        "mediagoblin.oauth.views:access_token"
        )

