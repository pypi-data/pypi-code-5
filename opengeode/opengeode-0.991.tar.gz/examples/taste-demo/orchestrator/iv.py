#! /usr/bin/python

Ada, C, GUI, SIMULINK, VHDL, OG, RTDS, SYSTEM_C, SCADE6 = range(9)
thread, passive, unknown = range(3)
PI, RI = range(2)
synch, asynch = range(2)
param_in, param_out = range(2)
UPER, NATIVE, ACN = range(3)
cyclic, sporadic, variator, protected, unprotected = range(5)
enumerated, sequenceof, sequence, set, setof, integer, boolean, real, choice, octetstring, string = range(11)
functions = {}

functions['orchestrator'] = {
    'name_with_case' : 'orchestrator',
    'runtime_nature': thread,
    'language': OG,
    'zipfile': '',
    'interfaces': {},
    'functional_states' : {}
}

functions['orchestrator']['interfaces']['pulse'] = {
    'port_name': 'pulse',
    'parent_fv': 'orchestrator',
    'direction': PI,
    'in': {},
    'out': {},
    'synchronism': asynch,
    'rcm': cyclic,
    'period': 1000,
    'wcet_low': 0,
    'wcet_low_unit': 'ms',
    'wcet_high': 0,
    'wcet_high_unit': 'ms',
    'distant_fv': '',
    'calling_threads': {},
    'distant_name': '',
    'queue_size': 1
}

functions['orchestrator']['interfaces']['pulse']['paramsInOrdered'] = []

functions['orchestrator']['interfaces']['pulse']['paramsOutOrdered'] = []

functions['orchestrator']['interfaces']['run'] = {
    'port_name': 'run',
    'parent_fv': 'orchestrator',
    'direction': PI,
    'in': {},
    'out': {},
    'synchronism': asynch,
    'rcm': variator,
    'period': 0,
    'wcet_low': 0,
    'wcet_low_unit': 'ms',
    'wcet_high': 0,
    'wcet_high_unit': 'ms',
    'distant_fv': '',
    'calling_threads': {},
    'distant_name': '',
    'queue_size': 1
}

functions['orchestrator']['interfaces']['run']['paramsInOrdered'] = ['cmd']

functions['orchestrator']['interfaces']['run']['paramsOutOrdered'] = []

functions['orchestrator']['interfaces']['run']['in']['cmd'] = {
    'type': 'MyInteger',
    'asn1_module': 'taste_dataview',
    'basic_type': integer,
    'asn1_filename': './dataview-uniq.asn',
    'encoding': NATIVE,
    'interface': 'run',
    'param_direction': param_in
}

functions['orchestrator']['interfaces']['housekeeping'] = {
    'port_name': 'housekeeping',
    'parent_fv': 'orchestrator',
    'direction': RI,
    'in': {},
    'out': {},
    'synchronism': asynch,
    'rcm': sporadic,
    'period': 0,
    'wcet_low': 0,
    'wcet_low_unit': '',
    'wcet_high': 0,
    'wcet_high_unit': '',
    'distant_fv': 'ground',
    'calling_threads': {},
    'distant_name': 'housekeeping',
    'queue_size': 1
}

functions['orchestrator']['interfaces']['housekeeping']['paramsInOrdered'] = ['hk']

functions['orchestrator']['interfaces']['housekeeping']['paramsOutOrdered'] = []

functions['orchestrator']['interfaces']['housekeeping']['in']['hk'] = {
    'type': 'MyInteger',
    'asn1_module': 'taste_dataview',
    'basic_type': integer,
    'asn1_filename': './dataview-uniq.asn',
    'encoding': NATIVE,
    'interface': 'housekeeping',
    'param_direction': param_in
}

functions['orchestrator']['interfaces']['computeGNC'] = {
    'port_name': 'computeGNC',
    'parent_fv': 'orchestrator',
    'direction': RI,
    'in': {},
    'out': {},
    'synchronism': synch,
    'rcm': unprotected,
    'period': 0,
    'wcet_low': 0,
    'wcet_low_unit': '',
    'wcet_high': 0,
    'wcet_high_unit': '',
    'distant_fv': 'passivefunction',
    'calling_threads': {},
    'distant_name': 'computeGNC',
    'queue_size': 1
}

functions['orchestrator']['interfaces']['computeGNC']['paramsInOrdered'] = ['inp']

functions['orchestrator']['interfaces']['computeGNC']['paramsOutOrdered'] = ['outp']

functions['orchestrator']['interfaces']['computeGNC']['in']['inp'] = {
    'type': 'MyInteger',
    'asn1_module': 'taste_dataview',
    'basic_type': integer,
    'asn1_filename': './dataview-uniq.asn',
    'encoding': NATIVE,
    'interface': 'computeGNC',
    'param_direction': param_in
}

functions['orchestrator']['interfaces']['computeGNC']['out']['outp'] = {
    'type': 'MyInteger',
    'asn1_module': 'taste_dataview',
    'basic_type': integer,
    'asn1_filename': './dataview-uniq.asn',
    'encoding': NATIVE,
    'interface': 'computeGNC',
    'param_direction': param_out
}

functions['ground'] = {
    'name_with_case' : 'ground',
    'runtime_nature': thread,
    'language': GUI,
    'zipfile': '',
    'interfaces': {},
    'functional_states' : {}
}

functions['ground']['interfaces']['housekeeping'] = {
    'port_name': 'housekeeping',
    'parent_fv': 'ground',
    'direction': PI,
    'in': {},
    'out': {},
    'synchronism': asynch,
    'rcm': sporadic,
    'period': 0,
    'wcet_low': 0,
    'wcet_low_unit': 'ms',
    'wcet_high': 0,
    'wcet_high_unit': 'ms',
    'distant_fv': '',
    'calling_threads': {},
    'distant_name': '',
    'queue_size': 1
}

functions['ground']['interfaces']['housekeeping']['paramsInOrdered'] = ['hk']

functions['ground']['interfaces']['housekeeping']['paramsOutOrdered'] = []

functions['ground']['interfaces']['housekeeping']['in']['hk'] = {
    'type': 'MyInteger',
    'asn1_module': 'taste_dataview',
    'basic_type': integer,
    'asn1_filename': './dataview-uniq.asn',
    'encoding': NATIVE,
    'interface': 'housekeeping',
    'param_direction': param_in
}

functions['ground']['interfaces']['run'] = {
    'port_name': 'run',
    'parent_fv': 'ground',
    'direction': RI,
    'in': {},
    'out': {},
    'synchronism': asynch,
    'rcm': sporadic,
    'period': 0,
    'wcet_low': 0,
    'wcet_low_unit': '',
    'wcet_high': 0,
    'wcet_high_unit': '',
    'distant_fv': 'orchestrator',
    'calling_threads': {},
    'distant_name': 'run',
    'queue_size': 1
}

functions['ground']['interfaces']['run']['paramsInOrdered'] = ['cmd']

functions['ground']['interfaces']['run']['paramsOutOrdered'] = []

functions['ground']['interfaces']['run']['in']['cmd'] = {
    'type': 'MyInteger',
    'asn1_module': 'taste_dataview',
    'basic_type': integer,
    'asn1_filename': './dataview-uniq.asn',
    'encoding': NATIVE,
    'interface': 'run',
    'param_direction': param_in
}

functions['passivefunction'] = {
    'name_with_case' : 'passiveFunction',
    'runtime_nature': passive,
    'language': C,
    'zipfile': '',
    'interfaces': {},
    'functional_states' : {}
}

functions['passivefunction']['interfaces']['computeGNC'] = {
    'port_name': 'computeGNC',
    'parent_fv': 'passivefunction',
    'direction': PI,
    'in': {},
    'out': {},
    'synchronism': synch,
    'rcm': unprotected,
    'period': 0,
    'wcet_low': 0,
    'wcet_low_unit': 'ms',
    'wcet_high': 0,
    'wcet_high_unit': 'ms',
    'distant_fv': '',
    'calling_threads': {},
    'distant_name': '',
    'queue_size': 1
}

functions['passivefunction']['interfaces']['computeGNC']['paramsInOrdered'] = ['inp']

functions['passivefunction']['interfaces']['computeGNC']['paramsOutOrdered'] = ['outp']

functions['passivefunction']['interfaces']['computeGNC']['in']['inp'] = {
    'type': 'MyInteger',
    'asn1_module': 'taste_dataview',
    'basic_type': integer,
    'asn1_filename': './dataview-uniq.asn',
    'encoding': NATIVE,
    'interface': 'computeGNC',
    'param_direction': param_in
}

functions['passivefunction']['interfaces']['computeGNC']['out']['outp'] = {
    'type': 'MyInteger',
    'asn1_module': 'taste_dataview',
    'basic_type': integer,
    'asn1_filename': './dataview-uniq.asn',
    'encoding': NATIVE,
    'interface': 'computeGNC',
    'param_direction': param_out
}
