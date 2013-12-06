# Copyright 2011-2013 GRNET S.A. All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
#   1. Redistributions of source code must retain the above
#      copyright notice, this list of conditions and the following
#      disclaimer.
#
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY GRNET S.A. ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL GRNET S.A OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and
# documentation are those of the authors and should not be
# interpreted as representing official policies, either expressed
# or implied, of GRNET S.A.

from io import StringIO
from pydoc import pager

from kamaki.cli import command
from kamaki.cli.command_tree import CommandTree
from kamaki.cli.errors import (
    CLIBaseUrlError, CLIInvalidArgument, raiseCLIError)
from kamaki.clients.cyclades import CycladesNetworkClient
from kamaki.cli.argument import (
    FlagArgument, ValueArgument, RepeatableArgument, IntArgument)
from kamaki.cli.commands import _command_init, errors, addLogSettings
from kamaki.cli.commands import (
    _optional_output_cmd, _optional_json, _name_filter, _id_filter)
from kamaki.cli.utils import filter_dicts_by_dict
from kamaki.cli.commands.cyclades import _service_wait


network_cmds = CommandTree('network', 'Networking API network commands')
port_cmds = CommandTree('port', 'Networking API network commands')
subnet_cmds = CommandTree('subnet', 'Networking API network commands')
ip_cmds = CommandTree('ip', 'Networking API floatingip commands')
_commands = [network_cmds, port_cmds, subnet_cmds, ip_cmds]


about_authentication = '\nUser Authentication:\
    \n* to check authentication: /user authenticate\
    \n* to set authentication token: /config set cloud.<cloud>.token <token>'


class _port_wait(_service_wait):

    def _wait(self, port_id, current_status, timeout=60):
        super(_port_wait, self)._wait(
            'Port', port_id, self.client.wait_port, current_status,
            timeout=timeout)


class _init_network(_command_init):
    @errors.generic.all
    @addLogSettings
    def _run(self, service='network'):
        if getattr(self, 'cloud', None):
            base_url = self._custom_url(service) or self._custom_url(
                'network')
            if base_url:
                token = self._custom_token(service) or self._custom_token(
                    'network') or self.config.get_cloud('token')
                self.client = CycladesNetworkClient(
                  base_url=base_url, token=token)
                return
        else:
            self.cloud = 'default'
        if getattr(self, 'auth_base', False):
            network_endpoints = self.auth_base.get_service_endpoints(
                self._custom_type('network') or 'network',
                self._custom_version('network') or '')
            base_url = network_endpoints['publicURL']
            token = self.auth_base.token
            self.client = CycladesNetworkClient(base_url=base_url, token=token)
        else:
            raise CLIBaseUrlError(service='network')

    def main(self):
        self._run()


@command(network_cmds)
class network_list(_init_network, _optional_json, _name_filter, _id_filter):
    """List networks
    Use filtering arguments (e.g., --name-like) to manage long server lists
    """

    arguments = dict(
        detail=FlagArgument('show detailed output', ('-l', '--details')),
        more=FlagArgument(
            'output results in pages (-n to set items per page, default 10)',
            '--more'),
        user_id=ValueArgument(
            'show only networks belonging to user with this id', '--user-id')
    )

    def _filter_by_user_id(self, nets):
        return filter_dicts_by_dict(nets, dict(user_id=self['user_id'])) if (
            self['user_id']) else nets

    @errors.generic.all
    @errors.cyclades.connection
    def _run(self):
        nets = self.client.list_networks()
        nets = self._filter_by_user_id(nets)
        nets = self._filter_by_name(nets)
        nets = self._filter_by_id(nets)
        if not self['detail']:
            nets = [dict(
                id=n['id'], name=n['name'], links=n['links']) for n in nets]
        kwargs = dict()
        if self['more']:
            kwargs['out'] = StringIO()
            kwargs['title'] = ()
        self._print(nets, **kwargs)
        if self['more']:
            pager(kwargs['out'].getvalue())

    def main(self):
        super(self.__class__, self)._run()
        self._run()


@command(network_cmds)
class network_info(_init_network, _optional_json):
    """Get details about a network"""

    @errors.generic.all
    @errors.cyclades.connection
    @errors.cyclades.network_id
    def _run(self, network_id):
        net = self.client.get_network_details(network_id)
        self._print(net, self.print_dict)

    def main(self, network_id):
        super(self.__class__, self)._run()
        self._run(network_id=network_id)


class NetworkTypeArgument(ValueArgument):

    types = ('MAC_FILTERED', 'CUSTOM', 'IP_LESS_ROUTED', 'PHYSICAL_VLAN')

    @property
    def value(self):
        return getattr(self, '_value', self.types[0])

    @value.setter
    def value(self, new_value):
        if new_value and new_value.upper() in self.types:
            self._value = new_value.upper()
        elif new_value:
            raise CLIInvalidArgument(
                'Invalid network type %s' % new_value, details=[
                    'Valid types: %s' % ', '.join(self.types), ])


@command(network_cmds)
class network_create(_init_network, _optional_json):
    """Create a new network (default type: MAC_FILTERED)"""

    arguments = dict(
        name=ValueArgument('Network name', '--name'),
        shared=FlagArgument(
            'Make network shared (special privileges required)', '--shared'),
        network_type=NetworkTypeArgument(
            'Valid network types: %s' % (', '.join(NetworkTypeArgument.types)),
            '--type')
    )

    @errors.generic.all
    @errors.cyclades.connection
    @errors.cyclades.network_type
    def _run(self, network_type):
        net = self.client.create_network(
            network_type, name=self['name'], shared=self['shared'])
        self._print(net, self.print_dict)

    def main(self):
        super(self.__class__, self)._run()
        self._run(network_type=self['network_type'])


@command(network_cmds)
class network_delete(_init_network, _optional_output_cmd):
    """Delete a network"""

    @errors.generic.all
    @errors.cyclades.connection
    @errors.cyclades.network_id
    def _run(self, network_id):
        r = self.client.delete_network(network_id)
        self._optional_output(r)

    def main(self, network_id):
        super(self.__class__, self)._run()
        self._run(network_id=network_id)


@command(network_cmds)
class network_modify(_init_network, _optional_json):
    """Modify network attributes"""

    arguments = dict(new_name=ValueArgument('Rename the network', '--name'))
    required = ['new_name', ]

    @errors.generic.all
    @errors.cyclades.connection
    @errors.cyclades.network_id
    def _run(self, network_id):
        r = self.client.update_network(network_id, name=self['new_name'])
        self._print(r, self.print_dict)

    def main(self, network_id):
        super(self.__class__, self)._run()
        self._run(network_id=network_id)


@command(subnet_cmds)
class subnet_list(_init_network, _optional_json, _name_filter, _id_filter):
    """List subnets
    Use filtering arguments (e.g., --name-like) to manage long server lists
    """

    arguments = dict(
        detail=FlagArgument('show detailed output', ('-l', '--details')),
        more=FlagArgument(
            'output results in pages (-n to set items per page, default 10)',
            '--more')
    )

    @errors.generic.all
    @errors.cyclades.connection
    def _run(self):
        nets = self.client.list_subnets()
        nets = self._filter_by_name(nets)
        nets = self._filter_by_id(nets)
        if not self['detail']:
            nets = [dict(
                id=n['id'], name=n['name'], links=n['links']) for n in nets]
        kwargs = dict()
        if self['more']:
            kwargs['out'] = StringIO()
            kwargs['title'] = ()
        self._print(nets, **kwargs)
        if self['more']:
            pager(kwargs['out'].getvalue())

    def main(self):
        super(self.__class__, self)._run()
        self._run()


@command(subnet_cmds)
class subnet_info(_init_network, _optional_json):
    """Get details about a subnet"""

    @errors.generic.all
    @errors.cyclades.connection
    def _run(self, subnet_id):
        net = self.client.get_subnet_details(subnet_id)
        self._print(net, self.print_dict)

    def main(self, subnet_id):
        super(self.__class__, self)._run()
        self._run(subnet_id=subnet_id)


class AllocationPoolArgument(RepeatableArgument):

    @property
    def value(self):
        return super(AllocationPoolArgument, self).value or []

    @value.setter
    def value(self, new_pools):
        new_list = []
        for pool in new_pools:
            start, comma, end = pool.partition(',')
            if not (start and comma and end):
                raise CLIInvalidArgument(
                    'Invalid allocation pool argument %s' % pool, details=[
                    'Allocation values must be of the form:',
                    '  <start address>,<end address>'])
            new_list.append(dict(start=start, end=end))
        self._value = new_list


@command(subnet_cmds)
class subnet_create(_init_network, _optional_json):
    """Create a new subnet"""

    arguments = dict(
        name=ValueArgument('Subnet name', '--name'),
        allocation_pools=AllocationPoolArgument(
            'start_address,end_address of allocation pool (can be repeated)'
            ' e.g., --alloc-pool=123.45.67.1,123.45.67.8',
            '--alloc-pool'),
        gateway=ValueArgument('Gateway IP', '--gateway'),
        subnet_id=ValueArgument('The id for the subnet', '--id'),
        ipv6=FlagArgument('If set, IP version is set to 6, else 4', '--ipv6'),
        enable_dhcp=FlagArgument('Enable dhcp (default: off)', '--with-dhcp'),
        network_id=ValueArgument('Set the network ID', '--network-id'),
        cidr=ValueArgument('Set the CIDR', '--cidr')
    )
    required = ('network_id', 'cidr')

    @errors.generic.all
    @errors.cyclades.connection
    @errors.cyclades.network_id
    def _run(self, network_id, cidr):
        net = self.client.create_subnet(
            network_id, cidr,
            self['name'], self['allocation_pools'], self['gateway'],
            self['subnet_id'], self['ipv6'], self['enable_dhcp'])
        self._print(net, self.print_dict)

    def main(self):
        super(self.__class__, self)._run()
        self._run(network_id=self['network_id'], cidr=self['cidr'])


# @command(subnet_cmds)
# class subnet_delete(_init_network, _optional_output_cmd):
#     """Delete a subnet"""

#     @errors.generic.all
#     @errors.cyclades.connection
#     def _run(self, subnet_id):
#         r = self.client.delete_subnet(subnet_id)
#         self._optional_output(r)

#     def main(self, subnet_id):
#         super(self.__class__, self)._run()
#         self._run(subnet_id=subnet_id)


@command(subnet_cmds)
class subnet_modify(_init_network, _optional_json):
    """Modify the attributes of a subnet"""

    arguments = dict(
        new_name=ValueArgument('New name of the subnet', '--name')
    )
    required = ['new_name']

    @errors.generic.all
    @errors.cyclades.connection
    def _run(self, subnet_id):
        r = self.client.get_subnet_details(subnet_id)
        r = self.client.update_subnet(
            subnet_id, r['network_id'], name=self['new_name'])
        self._print(r, self.print_dict)

    def main(self, subnet_id):
        super(self.__class__, self)._run()
        self._run(subnet_id=subnet_id)


@command(port_cmds)
class port_list(_init_network, _optional_json):
    """List all ports"""

    @errors.generic.all
    @errors.cyclades.connection
    def _run(self):
        net = self.client.list_ports()
        self._print(net)

    def main(self):
        super(self.__class__, self)._run()
        self._run()


@command(port_cmds)
class port_info(_init_network, _optional_json):
    """Get details about a port"""

    @errors.generic.all
    @errors.cyclades.connection
    def _run(self, port_id):
        net = self.client.get_port_details(port_id)
        self._print(net, self.print_dict)

    def main(self, port_id):
        super(self.__class__, self)._run()
        self._run(port_id=port_id)


@command(port_cmds)
class port_delete(_init_network, _optional_output_cmd, _port_wait):
    """Delete a port (== disconnect server from network)"""

    arguments = dict(
        wait=FlagArgument('Wait port to be established', ('-w', '--wait'))
    )

    @errors.generic.all
    @errors.cyclades.connection
    def _run(self, port_id):
        r = self.client.delete_port(port_id)
        if self['wait']:
            self._wait(r['id'], r['status'])
        self._optional_output(r)

    def main(self, port_id):
        super(self.__class__, self)._run()
        self._run(port_id=port_id)


@command(port_cmds)
class port_modify(_init_network, _optional_json):
    """Modify the attributes of a port"""

    arguments = dict(new_name=ValueArgument('New name of the port', '--name'))
    required = ['new_name', ]

    @errors.generic.all
    @errors.cyclades.connection
    def _run(self, port_id):
        r = self.client.get_port_details(port_id)
        r = self.client.update_port(
            port_id, r['network_id'], name=self['new_name'])
        self._print(r, self.print_dict)

    def main(self, port_id):
        super(self.__class__, self)._run()
        self._run(port_id=port_id)


class _port_create(_init_network, _optional_json, _port_wait):

    def connect(self, network_id, device_id):
        fixed_ips = [dict(
            subnet_id=self['subnet_id'], ip_address=self['ip_address'])] if (
                self['subnet_id']) else None
        r = self.client.create_port(
            network_id, device_id,
            name=self['name'],
            security_groups=self['security_group_id'],
            fixed_ips=fixed_ips)
        if self['wait']:
            self._wait(r['id'], r['status'])
        self._print(r, self.print_dict)


@command(port_cmds)
class port_create(_port_create):
    """Create a new port (== connect server to network)"""

    arguments = dict(
        name=ValueArgument('A human readable name', '--name'),
        security_group_id=RepeatableArgument(
            'Add a security group id (can be repeated)',
            ('-g', '--security-group')),
        subnet_id=ValueArgument(
            'Subnet id for fixed ips (used with --ip-address)',
            '--subnet-id'),
        ip_address=ValueArgument(
            'IP address for subnet id (used with --subnet-id', '--ip-address'),
        network_id=ValueArgument('Set the network ID', '--network-id'),
        device_id=ValueArgument(
            'The device is either a virtual server or a virtual router',
            '--device-id'),
        wait=FlagArgument('Wait port to be established', ('-w', '--wait')),
    )
    required = ('network_id', 'device_id')

    @errors.generic.all
    @errors.cyclades.connection
    @errors.cyclades.network_id
    @errors.cyclades.server_id
    def _run(self, network_id, server_id):
        self.connect(network_id, server_id)

    def main(self):
        super(self.__class__, self)._run()
        self._run(network_id=self['network_id'], server_id=self['device_id'])


@command(port_cmds)
class port_wait(_init_network, _port_wait):
    """Wait for port to finish [ACTIVE, DOWN, BUILD, ERROR]"""

    arguments = dict(
        timeout=IntArgument(
            'Wait limit in seconds (default: 60)', '--timeout', default=60)
    )

    @errors.generic.all
    @errors.cyclades.connection
    def _run(self, port_id, current_status):
        port = self.client.get_port_details(port_id)
        if port['status'].lower() == current_status.lower():
            self._wait(port_id, current_status, timeout=self['timeout'])
        else:
            self.error(
                'Port %s: Cannot wait for status %s, '
                'status is already %s' % (
                    port_id, current_status, port['status']))

    def main(self, port_id, current_status='BUILD'):
        super(self.__class__, self)._run()
        self._run(port_id=port_id, current_status=current_status)


@command(ip_cmds)
class ip_list(_init_network, _optional_json):
    """List reserved floating IPs"""

    @errors.generic.all
    @errors.cyclades.connection
    def _run(self):
        self._print(self.client.list_floatingips())

    def main(self):
        super(self.__class__, self)._run()
        self._run()


@command(ip_cmds)
class ip_info(_init_network, _optional_json):
    """Get details on a floating IP"""

    @errors.generic.all
    @errors.cyclades.connection
    def _run(self, ip_id):
        self._print(
            self.client.get_floatingip_details(ip_id), self.print_dict)

    def main(self, ip_id):
        super(self.__class__, self)._run()
        self._run(ip_id=ip_id)


@command(ip_cmds)
class ip_create(_init_network, _optional_json):
    """Reserve an IP on a network"""

    arguments = dict(
        network_id=ValueArgument(
            'The network to preserve the IP on', '--network-id'),
        ip_address=ValueArgument('Allocate a specific IP address', '--address')
    )
    required = ('network_id', )

    @errors.generic.all
    @errors.cyclades.connection
    @errors.cyclades.network_id
    def _run(self, network_id):
        self._print(
            self.client.create_floatingip(
                network_id, floating_ip_address=self['ip_address']),
            self.print_dict)

    def main(self):
        super(self.__class__, self)._run()
        self._run(network_id=self['network_id'])


@command(ip_cmds)
class ip_delete(_init_network, _optional_output_cmd):
    """Unreserve an IP (also delete the port, if attached)"""

    def _run(self, ip_id):
        self._optional_output(self.client.delete_floatingip(ip_id))

    def main(self, ip_id):
        super(self.__class__, self)._run()
        self._run(ip_id=ip_id)


#  Warn users for some importand changes

@command(network_cmds)
class network_connect(_port_create):
    """Connect a network with a device (server or router)"""

    arguments = dict(
        name=ValueArgument('A human readable name for the port', '--name'),
        security_group_id=RepeatableArgument(
            'Add a security group id (can be repeated)',
            ('-g', '--security-group')),
        subnet_id=ValueArgument(
            'Subnet id for fixed ips (used with --ip-address)',
            '--subnet-id'),
        ip_address=ValueArgument(
            'IP address for subnet id (used with --subnet-id', '--ip-address'),
        wait=FlagArgument('Wait network to connect', ('-w', '--wait')),
    )

    @errors.generic.all
    @errors.cyclades.connection
    @errors.cyclades.network_id
    @errors.cyclades.server_id
    def _run(self, network_id, server_id):
        self.connect(network_id, server_id)

    def main(self, network_id, device_id):
        super(self.__class__, self)._run()
        self._run(network_id=network_id, device_id=device_id)


@command(network_cmds)
class network_disconnect(_init_network, _port_wait, _optional_json):
    """Disconnnect a network from a device"""

    def _cyclades_client(self):
        auth = getattr(self, 'auth_base')
        endpoints = auth.get_service_endpoints('compute')
        URL = endpoints['publicURL']
        from kamaki.clients.cyclades import CycladesClient
        return CycladesClient(URL, self.client.token)

    arguments = dict(
        wait=FlagArgument('Wait network to disconnect', ('-w', '--wait'))
    )

    @errors.generic.all
    @errors.cyclades.connection
    @errors.cyclades.network_id
    @errors.cyclades.server_id
    def _run(self, network_id, device_id):
        vm = self._cyclades_client().get_server_details(device_id)
        nets = [net for net in vm['attachments'] if net['network_id'] not in (
            'network_id', )]
        if not nets:
            raiseCLIError('Network %s is not connected to device %s' % (
                network_id, device_id))
        for net in nets:
            self.client.port_delete(net['id'])
            self.error('Deleting this connection:')
            self.print_dict(net)
            if self['wait']:
                self._wait(net['id'], net['status'])

    def main(self, network_id, device_id):
        super(self.__class__, self)._run()
        self._run(network_id=network_id, device_id=device_id)
