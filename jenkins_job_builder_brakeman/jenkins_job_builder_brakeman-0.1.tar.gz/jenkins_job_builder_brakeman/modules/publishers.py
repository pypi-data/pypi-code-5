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


def brakeman(parser, xml_parent, data):
    """yaml: brakeman
    Enable parsing of brakeman reports

    :arg str output: path for the brakeman output file

    Example::

      publishers:
        - brakeman:
            output: bob.tabs
    """
    logger = logging.getLogger("%s:brakeman" % __name__)
    brakeman = XML.SubElement(xml_parent, 'hudson.plugins.brakeman.BrakemanPublisher')
    XML.SubElement(brakeman, 'outputFile').text = data['output']
