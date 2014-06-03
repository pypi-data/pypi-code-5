#!/usr/bin/env python

import sys
from config import load_config, install_basic_config, DEFAULT_CONFIG_PATH
import db

def cursed_lich_server():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', metavar='CONFIG_PATH',
        default=DEFAULT_CONFIG_PATH,
        help='run server with configuration')
    subs = parser.add_subparsers(dest='cmd')

    cmd_runserver = subs.add_parser('start', help='Start server')
    cmd_runserver.add_argument('--debug', '-d', action='store_true',
        help='Enable debug logging. Default logging set via configuration '
        'file')

    cmd_installconfig = subs.add_parser('installconfig',
        help='Install default config file')

    cmd_genkeys = subs.add_parser('genkeys',
        help='Generate SSL key and cert')

    cmd_adduser = subs.add_parser('adduser', help='add new user')
    cmd_adduser.add_argument('username')
    cmd_adduser.add_argument('password')

    cmd_addhero = subs.add_parser('addhero', help='add new hero')
    cmd_addhero.add_argument('username')
    cmd_addhero.add_argument('heroname')
    cmd_addhero.add_argument('posx', type=int, default=1, 
        help='starting x location')
    cmd_addhero.add_argument('posy', type=int, default=1,
        help='starting y location')

    args = parser.parse_args()

    if args.cmd == 'installconfig':
        install_basic_config(path=args.config)
        print('Installed config to %s' % args.config)
        print('Run "cursed_lich_server genkeys" to generate SSL key files.')

    # Important to install the config before loading it first.
    config = load_config(args.config)
    config.get_session = db.create_session(config.DB_PATH)
    config.sesh = config.get_session()

    if args.cmd == 'genkeys':
        import subprocess
        out = subprocess.check_output((
            'openssl req -x509 -nodes -days 1095 -newkey rsa:2048 -keyout '
            '%s -out %s' % (config.SSL_KEY_PATH, config.SSL_CERT_PATH))
            .split())
        print(out)
        print('Generated keypair good for 3 years to:\nKey: %s\nCert: %s' %
            (config.SSL_KEY_PATH, config.SSL_CERT_PATH))
    if args.cmd in ['installconfig', 'genkeys']:
        print('Generating configuration files complete. Now run:')
        print('$ cursed_lich_server start')
        sys.exit(0)

    if args.cmd == 'adduser':
        user = db.add_user(config.sesh, args.username, args.password)
        config.logger.info('Created %s' % str(user))
    elif args.cmd == 'addhero':
        hero = db.add_hero(config.sesh, args.username, args.heroname,
            start_pos=(args.posx, args.posy))
        config.logger.info('Created %s' % str(hero))
    elif args.cmd == 'start':
        if args.debug:
            config.set_debug_mode()
            config.logger.debug('Debug mode on.')
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

if __name__ == '__main__':
    cursed_lich_server()
