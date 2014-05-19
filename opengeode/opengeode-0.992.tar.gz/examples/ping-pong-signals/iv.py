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

functions['ping'] = {
    'runtime_nature': thread,
    'language': OG,
    'zipfile': '',
    'interfaces': {}
}

functions['ping']['interfaces']['activation'] = {
    'port_name': 'activation',
    'parent_fv': 'ping',
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

functions['ping']['interfaces']['activation']['paramsInOrdered'] = []

functions['ping']['interfaces']['activation']['paramsOutOrdered'] = []

functions['ping']['interfaces']['snd_ping'] = {
    'port_name': 'snd_ping',
    'parent_fv': 'ping',
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
    'distant_fv': 'pong',
    'calling_threads': {},
    'distant_name': 'recv_ping',
    'queue_size': 1
}

functions['ping']['interfaces']['snd_ping']['paramsInOrdered'] = []

functions['ping']['interfaces']['snd_ping']['paramsOutOrdered'] = []

functions['pong'] = {
    'runtime_nature': thread,
    'language': OG,
    'zipfile': '',
    'interfaces': {}
}

functions['pong']['interfaces']['recv_ping'] = {
    'port_name': 'recv_ping',
    'parent_fv': 'pong',
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

functions['pong']['interfaces']['recv_ping']['paramsInOrdered'] = []

functions['pong']['interfaces']['recv_ping']['paramsOutOrdered'] = []
