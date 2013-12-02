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

from mediagoblin.tools.staticdirect import PluginStatic
from mediagoblin.tools import pluginapi
from pkg_resources import resource_filename

def setup_plugin():
    routes = [
        ('staticstuff.static_demo',
         '/staticstuff/',
         'mediagoblin.tests.testplugins.staticstuff.views:static_demo')]

    pluginapi.register_routes(routes)


hooks = {
    'setup': setup_plugin,
    'static_setup': lambda: PluginStatic(
        'staticstuff',
        resource_filename(
            'mediagoblin.tests.testplugins.staticstuff',
            'static'))}
