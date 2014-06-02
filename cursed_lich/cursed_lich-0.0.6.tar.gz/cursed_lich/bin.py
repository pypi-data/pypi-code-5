#!/usr/bin/env python

import sys
from config import load_config, install_basic_config, DEFAULT_CONFIG_PATH

def cursed_lich_server():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', metavar='CONFIG_PATH',
        default=DEFAULT_CONFIG_PATH,
        help='run server with configuration')
    parser.add_argument('--install-config', action='store_true',
        help='install the basic configuration file, defaults to %s' % (
        DEFAULT_CONFIG_PATH))
    parser.add_argument('--gen-ssl-key', '-g', action='store_true',
        help='generate SSL key and cert using OpenSSL for hosting SSL')
    parser.add_argument('--debug', '-d', action='store_true',
        help='Enable debug logging. Default logging set via configuration '
        'file')
    args = parser.parse_args()
    if args.install_config:
        install_basic_config(path=args.config)
        print('Installed config to %s' % args.config)
        print('Run --gen-ssl-key/-g to generate SSL, and edit config '
            'with USE_SSL=True.')
    # Important to install the config before loading it first.
    config = load_config(args.config)
    if args.debug:
        config.set_debug_mode()
        config.logger.debug('Debug mode on.')
    if args.gen_ssl_key:
        import subprocess
        out = subprocess.check_output((
            'openssl req -x509 -nodes -days 1095 -newkey rsa:2048 -keyout '
            '%s -out %s' % (config.SSL_KEY_PATH, config.SSL_CERT_PATH))
            .split())
        print(out)
        print('Generated keypair good for 3 years to:\nKey: %s\nCert: %s' %
            (config.SSL_KEY_PATH, config.SSL_CERT_PATH))
    if args.gen_ssl_key or args.install_config:
        print('Generating configuration files complete. Please run again to '
            'start server.')
        sys.exit(0)
    import server
    server.init_server(config)

def cursed_lich():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default=9900,
        help='Destination listening port')
    parser.add_argument('addr', metavar='IP_OR_HOSTNAME', 
        help='Destination address')
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('--insecure', '-i', action='store_true',
        help='doesnt use SSL. Wont work with most servers. (please use SSL)')
    args = parser.parse_args()
    import client
    client.init_client(args.addr, args.port, args.username, args.password,
        insecure=args.insecure)

