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

nginx_configuration = """
server {
 #################################################
 # """+_("Stock useful config options, but ignore them :)")+"""
 #################################################
 include /etc/nginx/mime.types;

 autoindex off;
 default_type  application/octet-stream;
 sendfile on;

 # Gzip
 gzip on;
 gzip_min_length 1024;
 gzip_buffers 4 32k;
 gzip_types text/plain text/html application/x-javascript text/javascript text/xml text/css;

 #####################################
 # """+_("Mounting MediaGoblin stuff")+"""
 # """+_("This is the section you should read")+"""
 #####################################

 # """+_("Change this to update the upload size limit for your users")+"""
 client_max_body_size 8m;

 # """+_("prevent attacks (someone uploading a .txt file that the browser")+"""
 # """+_("interprets as an HTML file, etc.)")+"""
 add_header X-Content-Type-Options nosniff;

 server_name {server_name} www.{server_name};
 access_log /var/log/nginx/{server_name}.access.log;
 error_log /var/log/nginx/{server_name}.example.error.log;

 # """+_("MediaGoblin's stock static files: CSS, JS, etc.")+"""
 location /mgoblin_static/ {
    alias {directory_path}/mediagoblin/static/;
 }

 # """+_("Instance specific media:")+"""
 location /mgoblin_media/ {
    alias {directory_path}/user_dev/media/public/;
 }

 # """+_("Theme static files (usually symlinked in)")+"""
 location /theme_static/ {
    alias {directory_path}/user_dev/theme_static/;
 }

 # """+_("Plugin static files (usually symlinked in)")+"""
 location /plugin_static/ {
    alias {directory_path}/user_dev/plugin_static/;
 }

 # """+_("Mounting MediaGoblin itself via FastCGI.")+"""
 location / {
    fastcgi_pass 127.0.0.1:26543;
    include /etc/nginx/fastcgi_params;

    # """+_("our understanding vs nginx's handling of script_name vs")+"""
    # """+_("path_info don't match :)")+"""
    fastcgi_param PATH_INFO $fastcgi_script_name;
    fastcgi_param SCRIPT_NAME "";
 }
}
"""

def get_nginx_configuration(server_name, directory_path):
    output = """server {
 #################################################
 # """+_("Stock useful config options, but ignore them :)")+"""
 #################################################
 include /etc/nginx/mime.types;

 autoindex off;
 default_type  application/octet-stream;
 sendfile on;

 # Gzip
 gzip on;
 gzip_min_length 1024;
 gzip_buffers 4 32k;
 gzip_types text/plain text/html application/x-javascript text/javascript text/xml text/css;

 #####################################
 # """+_("Mounting MediaGoblin stuff")+"""
 # """+_("This is the section you should read")+"""
 #####################################

 # """+_("Change this to update the upload size limit for your users")+"""
 client_max_body_size 8m;

 # """+_("prevent attacks (someone uploading a .txt file that the browser")+"""
 # """+_("interprets as an HTML file, etc.)")+"""
 add_header X-Content-Type-Options nosniff;
"""
    output +=  """
 server_name {server_name} www.{server_name};
 access_log /var/log/nginx/{server_name}.access.log;
 error_log /var/log/nginx/{server_name}.example.error.log;

 # """.format(server_name=server_name)
    output += _("MediaGoblin's stock static files: CSS, JS, etc.")
    output += """
 location /mgoblin_static/ {
"""
    output += "    alias {directory_path}/mediagoblin/static/;".format(
        directory_path=directory_path)
    output += """
}

 # """ + _("Instance specific media:") + """
 location /mgoblin_media/ {
"""
    output += "    alias {directory_path}/user_dev/media/public/;".format(
        directory_path=directory_path)
    output +="""
}

 # """ + _("Theme static files (usually symlinked in)") + """
 location /theme_static/ {
"""
    output += "    alias {directory_path}/user_dev/theme_static/;".format(
        directory_path=directory_path)
    output += """
}

 # """ + _("Plugin static files (usually symlinked in)") + """
  location /plugin_static/ {
"""
    output += """
}

 # """ + _("Mounting MediaGoblin itself via FastCGI.") + """
  location / {
    fastcgi_pass 127.0.0.1:26543;
    include /etc/nginx/fastcgi_params;

    #""" + _("our understanding vs nginx's handling of script_name vs")+"""
    #""" + _("path_info don't match :)")+"""
    fastcgi_param PATH_INFO $fastcgi_script_name;
    fastcgi_param SCRIPT_NAME "";
 }
}"""
    return output
