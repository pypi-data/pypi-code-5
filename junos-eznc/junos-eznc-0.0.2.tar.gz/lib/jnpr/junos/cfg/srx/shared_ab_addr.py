# 3rd-party modules
from lxml.builder import E 

# module packages
from ... import jxml as JXML
from .. import Resource

class SharedAddrBookAddr( Resource ):
  """
  [edit security address-book <ab_name> address <name>]

  Resource name: str
    <name> is the address item name

  Managed by: SharedAddrBook
    <ab_name> is the address book name, taken from parent resource    
  """
  PROPERTIES = [
    'description',
    'ip_prefix',
  ]

  def _xml_at_top(self):
    xml = self.P._xml_at_top()
    xml.find('.//address-book').append(E.address(self._name))
    return xml

  ##### -----------------------------------------------------------------------
  ##### XML reading
  ##### -----------------------------------------------------------------------

  def _xml_at_res(self, xml):
    return xml.find('.//address-book/address')

  def _xml_to_py(self, as_xml, to_py ):
    Resource._r_has_xml_status( as_xml, to_py )
    Resource.copyifexists( as_xml, 'description', to_py )
    to_py['ip_prefix'] = as_xml.find('ip-prefix').text

  ##### -----------------------------------------------------------------------
  ##### XML writing
  ##### -----------------------------------------------------------------------

  def _xml_change_ip_prefix(self, xml):
    xml.append(E('ip-prefix', self.should['ip_prefix']))
    return True

  ##### -----------------------------------------------------------------------
  ##### Manager List, Catalog
  ##### -----------------------------------------------------------------------

  def _r_list(self):
    # The parent keeps a property on this list, so just use it, yo!
    self._rlist = self.P['$addrs']

  def _r_catalog(self):
    get = self.P._xml_at_top()
    get.find('.//address-book').append(E('address'))
    got = self.J.rpc.get_config( get )
    for addr in got.xpath('.//address-book/address'):
      name = addr.find('name').text
      self._rcatalog[name] = {}
      self._xml_to_py( addr, self._rcatalog[name] )
