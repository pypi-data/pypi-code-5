# GNU MediaGoblin Easy Install Script
# Copyright (C) 2013, 2014 MediaGoblin contributors.
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
from gettext import gettext as _

INSTRUCTIONS = {
'linux_distro':
    {'question':_("""
What linux distribution are you using?"""),
    'responses':[
        _("A Debian-Based Distribution (ie. Ubuntu, LinuxMint, Debian)"),
        _("A Redhat-Based Distribution (ie. Fedora, CentOS)"),
        _("I'm using an OS other than linux")]},

'sql_database':
    {'question':_("""
We're deciding what type of database to use. Will your server be a small server 
or will it be often used by many users?"""),
    'responses':[_(
"""A Small Server that recieves little traffic (This will install SQLite3 as
your database management system)"""),
                 _(
"""Large or Medium server often viewed by many visitors (This will install PostGreSQL as your database management system)""")]},

'directory_name':_("""
What will you use as the domain name of the website you are setting up? For
instance you may enter:
> mediagoblin.thisisanexample.org. 

Please enter the domain name and the suffix (.com, .org, etc) but leave out the "www." and the "http://"
"""),

'directory_path':{
    'question':_("""
In what directory will you place your mediagoblin server?
Examples: /srv/ or /home/<your username>/"""),
    'responses':['/srv/<new directory>',
                 '/home/mediagoblin/<new directory>',
               _('I want to choose a different directory location')]},
'directory_path_other':
_("""
Where will you place this directory?
"""),
'system_email':
_("""
If you want all system-wide announcements to be sent from your email, enter it
here. If not, just press enter. (This can easily be changed later)
"""),
'serving_method':{
    'question':_("""
How would you like to serve your website?"""),
    'responses':[_('Locally, (Choose this if you just want to view the website yourself, such as for testing or development)'),
                 _('Using nginx (Choose this if you want your website to be accessible to users outside your network)')]}}
