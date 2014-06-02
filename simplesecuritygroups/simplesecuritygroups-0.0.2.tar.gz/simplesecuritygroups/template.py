import json
from collections import OrderedDict
import re
import six

# There's a lot of use of OrderedDicts, this is mainly to get the Cloudformation .json output
# outputting in a consistent sensible readable order
class SecurityGroups(object):
    def __init__(self, description="Security Group Stack", version="2010-09-09"):
        self.version = version
        self.description = description
        self.parameters = {}
        self.resources = []

    def add_parameter(self, name, description, type="String", default=None):
        param = OrderedDict([
            ("Description", description),
            ("Type", type)
        ])

        if default is not None:
            param["Default"] = default

        self.parameters[name] = param

        return self

    def add_resource(self, group):
        self.resources.append(group)
        return self

    def __str__(self):
        stack_json = OrderedDict()
        stack_json["AWSTemplateFormatVersion"] = self.version
        stack_json["Description"] = self.description
        stack_json["Parameters"] = self.parameters

        stack_json["Resources"] = OrderedDict()
        for group in self.resources:
            stack_json["Resources"][group.name] = group.to_jsonable()

        return pretty_json(stack_json)

    def ingress(self, source, protocol="both", ports="all", destinations=None, name=None):
        rules = self.get_rules(source, protocol, ports, destinations)

        for rule in rules:
            if name is None or len(rules) > 1:
                # this is probably going to generate invalid names when using IPs for destinations... look at representing IPs in AWS valid way?
                name = "SG%s%s%s%s%s" % (rule["source"], rule["protocol"], rule["destination"], rule["port_from"], rule["port_to"])

            self.add_resource(SecurityGroupIngress(name, rule["destination"], rule["protocol"], rule["source"], rule["port_from"], rule["port_to"]))

        return self

    def egress(self, source, protocol="both", ports="all", destinations=None, name=None):
        rules = self.get_rules(source, protocol, ports, destinations)

        for rule in rules:
            if name is None or len(rules) > 1:
                # this is probably going to generate invalid names when using IPs for destinations... look at representing IPs in AWS valid way?
                name = "SG%s%s%s%s%s" % (rule["source"], rule["protocol"], rule["destination"], rule["port_from"], rule["port_to"])

            self.add_resource(SecurityGroupEgress(name, rule["source"], rule["protocol"], rule["destination"], rule["port_from"], rule["port_to"]))

        return self

    # add an ingress and a matching egress rule
    # source isn't really optional here...  but dont' want a different parameter order than other methods
    def pair(self, from_group, protocol="both", ports="all", to_group=None, prefix=None):
        self.ingress(to_group, "tcp", ports, from_group, "%sIngress" % (prefix))
        self.egress(from_group, "tcp", ports, to_group, "%sEgress" % (prefix))

        return self


    def get_rules(self, source, protocol, ports, destinations):
        protocols = determine_protocols(protocol)
        port_ranges = determine_port_ranges(ports)

        if isinstance(destinations, six.string_types) or destinations is None:
            destinations = [destinations]

        rules = [{"source": source, "protocol": p, "destination": destination, "port_from": port_from, "port_to": port_to } for (port_from, port_to) in port_ranges for destination in destinations for p in protocols]

        return rules

        # .add_resource(SecurityGroupEgress("SGAEMPublisherInfraLog", "SGAEMPublisher", "tcp", "SGInfrastructureLog", RSYSLOG))
        # .add_resource(SecurityGroupIngress("SGAEMPublisherRsyncIngress", "SGAEMPublisher", "tcp", "SGAEMPublisher", 873))

class SecurityGroup(object):
    def __init__(self, name, description, VpcId):
        self.name = name
        self.description = description
        self.VpcId = VpcId
        self._ingress = []
        self._egress = []

    def __str__(self):
        return pretty_json({"name": self.name, "description": self.description, "VpcId": self.VpcId})

    def ingress(self, protocol="both", ports="all", destination=None):
        rules = self.get_rules(protocol, ports, destination, "SourceSecurityGroupId")
        self._ingress.extend(rules)

        return self

    def get_rules(self, protocol, ports, destinations, default_destination_type):
        protocols = determine_protocols(protocol)
        port_ranges = determine_port_ranges(ports)
        destinations_with_types = determine_destinations(destinations, default_destination_type)
        rules = [OrderedDict([("IpProtocol", p), ("FromPort", port_from), ("ToPort", port_to), (destination_type, destination)]) for (port_from, port_to) in port_ranges for (destination_type, destination) in destinations_with_types for p in protocols]

        return rules

    def egress(self, protocols="both", ports="all", source=None):
        rules = self.get_rules(protocols, ports, source, "DestinationSecurityGroupId")
        self._egress.extend(rules)

        return self

    def to_jsonable(self):
        properties = OrderedDict()
        properties["GroupDescription"] = self.description
        properties["VpcId"] = self.VpcId
        if len(self._ingress):
            properties["SecurityGroupIngress"] = self._ingress

        if len(self._egress):
            properties["SecurityGroupEgress"] = self._egress

        group_json  = OrderedDict([
            ("Type", "AWS::EC2::SecurityGroup"),
            ("Properties", properties)
        ])
        return group_json

class SecurityGroupRule(object):
    def __init__(self, name, source, protocol, destination, from_port, to_port=None):
        self.type = "" # child classes will specify this
        self.sg_type = "" # child classes will specify this

        self.name = name
        self.source = {"Ref": source }
        self.protocol = protocol
        self.from_port = str(from_port)
        if to_port is None:
            to_port = from_port
        self.to_port = str(to_port)
        self.destination = destination
        pass

    def to_jsonable(self):
        destination = self.destination
        destination_type = self.sg_type

        (destination_type, destination) = determine_destinations([self.destination], self.sg_type).pop()

        group_json = OrderedDict([
            ("Type", self.type),
            ("Properties", OrderedDict([
                ("GroupId", self.source),
                ("IpProtocol", self.protocol),
                ("FromPort", str(self.from_port)),
                ("ToPort", str(self.to_port)),
                (destination_type, destination)
            ]))
        ])
        return group_json

class SecurityGroupEgress(SecurityGroupRule):
    def __init__(self, name, source, protocol, destination, from_port, to_port=None):
        super(SecurityGroupEgress, self).__init__(name, source, protocol, destination, from_port, to_port)
        self.type = "AWS::EC2::SecurityGroupEgress"
        self.sg_type = "DestinationSecurityGroupId"

class SecurityGroupIngress(SecurityGroupRule):
    def __init__(self, name, destination, protocol, source, from_port, to_port=None):
        super(SecurityGroupIngress, self).__init__(name, source, protocol, destination, from_port, to_port)
        self.type = "AWS::EC2::SecurityGroupIngress"
        self.sg_type = "SourceSecurityGroupId"

def pretty_json(object):
    return json.dumps(object, indent=4, separators=(',', ': '))
    #jsonpickle.set_encoder_options('json', indent=4)
    #return jsonpickle.encode(object)

def determine_protocols(protocol):
    if protocol == "both":
        protocols = ["tcp", "udp"]
    else:
        protocols = [protocol]

    return protocols


def determine_destinations(destinations, default_destination_type):
    if isinstance(destinations, six.string_types) or destinations is None:
        destinations = [destinations]

    destinations_with_types = []
    for destination in destinations:
        destination_type = default_destination_type

        if destination == None:
            destination = "0.0.0.0/0"
            destination_type = "CidrIp"
        elif not re.match("\d*\.\d*\.\d*\.\d*/\d*", destination):
            #destination is probably a security group
            destination = { "Ref": destination}
        else:
            destination_type = "CidrIp"

        destinations_with_types.append((destination_type, destination))
    return destinations_with_types

def determine_port_ranges(ports):
    if isinstance(ports, (six.string_types + six.integer_types)):
        ports = [ports]

    port_ranges = []
    for port in ports:
        if port == "all":
            port_ranges.append(("0", "65535"))
        else:
            ports_bits = str(port).split('..')
            port_ranges.append((ports_bits[0], ports_bits.pop()))
    return port_ranges
