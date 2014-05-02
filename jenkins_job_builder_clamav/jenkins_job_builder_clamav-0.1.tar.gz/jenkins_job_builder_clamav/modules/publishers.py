#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import xml.etree.ElementTree as XML
import logging


"""
<org.jenkinsci.plugins.clamav.ClamAvRecorder plugin="clamav@0.2.1">
    <includes>**</includes>
</org.jenkinsci.plugins.clamav.ClamAvRecorder>
"""
def clamav(parser, xml_parent, data):
    """yaml: clamav
    Enable virus scanning of files with ClamAV

    :arg str includes: pattern match for files to scan

    Example::

      publishers:
        - clamav:
            includes: **
    """
    logger = logging.getLogger("%s:clamav" % __name__)
    clamav = XML.SubElement(xml_parent, 'org.jenkinsci.plugins.clamav.ClamAvRecorder')
    XML.SubElement(clamav, 'includes').text = data['includes']
