#!/usr/bin/env python

import os

from twisted import internet
import twisted.internet.protocol
import twisted.internet.reactor
import twisted.internet.ssl

from google.protobuf.message import DecodeError

import db
import terrain
import net_pb2

__version__ = 1

def get_sessions_user(sesh, session_id):
    ''' Check to see if session is valid for request '''
    session = sesh.query('Session').filter_by(
        request_session_id=session_id).first()
    if session is None:
        CursedLichServer.conf.logger.warning(
            'received request with invalid session id')
        return None
    return session.user

def invalid_user_request(sesh, user, req):
    ''' Need to check if the request is for a hero owned by the user '''
    if user is None:
        return False
    if False:
        CursedLichServer.conf.logger.warning(
            'someone tried to act as another user')
    return False

class CursedLichServer(internet.protocol.Protocol):
    ''' Servz '''
    conf = None
    def dataReceived(self, data):
        ''' Receive raw data '''
        req = net_pb2.Request()
        try:
            req.ParseFromString(data)
        except DecodeError:
            CursedLichServer.conf.logger.error(
                'server could not decode data from request: %s' 
                % data.encode('hex'))
            return
        res = net_pb2.Response()
        res.response_id = req.request_id
        res.version = __version__
        res.compatible = True
        res.typ = req.typ
        # default is success
        res.status = net_pb2.SC_SUCCESS
        # non login attempts need valid session id
        if req.typ != net_pb2.MT_LOGIN:
            user = get_sessions_user(CursedLichServer.conf.sesh, req)
            invalid = invalid_user_request(
                CursedLichServer.conf.sesh, user, req)
            if user is None or invalid:
                res.status = net_pb2.SC_INVALID_SESSION
                res.error = 'Invalid Session ID (expired or just bad)'
                self.transport.write(res.SerializeToString())
                return
        # login attempt
        if req.typ == net_pb2.MT_LOGIN:
            user = CursedLichServer.conf.sesh.query(db.User).filter_by(
                username=req.login_request.username).first()
            if user is None:
                res.status = net_pb2.SC_INVALID_CREDS
                res.error = 'Invalid username'
            else:
                auth = user.auth(req.login_request.password)
                if not auth:
                    res.status = net_pb2.SC_INVALID_CREDS
                    res.error = 'Invalid password'
            if res.status == net_pb2.SC_SUCCESS:
                res.login_response.session_id = os.urandom(16).encode('base64')
        # get info on heroes
        elif req.typ == net_pb2.MT_INFO_HERO:
            pass
        # create a new hero
        elif req.typ == net_pb2.MT_CREATE_HERO:
            pass
        # perform an action, like move a hero
        elif req.typ == net_pb2.MT_ACTION:
            pass
        # Malformed request or non compatible versions
        else:
            res.status = net_pb2.SC_INVALID_REQUEST_TYPE
        self.transport.write(res.SerializeToString())

def run_init_checks(config):
    ''' Check certain variables for ability to run '''
    if config.USE_SSL:
        ssl_err = False
        if not os.path.isfile(config.SSL_KEY_PATH):
            config.logger.error(
                'File doesnt exist: %s' % config.SSL_KEY_PATH)
            ssl_err = True
        if not os.path.isfile(config.SSL_CERT_PATH):
            config.logger.error(
                'File doesnt exist: %s' % config.SSL_CERT_PATH)
            ssl_err = True
        if ssl_err:
            config.logger.error(
                'SSL enabled but cert/key files missing.\nPlease edit your '
                'config at %s' % config.path)
            return ssl_err
    # No error.
    config.logger.debug('run_init_checks completed successfully.')
    return False

def init_map(config):
    ''' Set up Cells in DB '''
    config.logger.warning('world not populated with Terrain. Populating...')
    cells = terrain.Terrain.create_terrain(
        config.WIDTH, config.HEIGHT, config.Z_Level.MIDGAARD)
    config.logger.info('Completed creating map. Writing to database...')
    config.sesh.add_all(cells)
    config.sesh.commit()
    config.logger.debug('Committed cells to database')

def init_world(config):
    ''' Set up and save database session '''
    config.logger.info('Initializing world')
    config.get_session = db.create_session(config.DB_PATH)
    config.sesh = config.get_session()
    if config.sesh.query(db.Cell).count() < config.WIDTH * config.HEIGHT:
        init_map(config)
    config.logger.info('DB map populated.')

def init_server(config):
    ''' Initialize listener '''
    config.logger.debug('Initializing server.')
    if run_init_checks(config):
        config.logger.error('Please fix errors and restart.')
        return
    factory = internet.protocol.Factory()
    CursedLichServer.conf = config
    factory.protocol = CursedLichServer
    if config.USE_SSL:
        internet.reactor.listenSSL(config.SERVER_PORT, factory,
            internet.ssl.DefaultOpenSSLContextFactory(
            config.SSL_KEY_PATH,
            config.SSL_CERT_PATH))
    else:
        internet.reactor.listenTCP(config.SERVER_PORT, factory)
    internet.reactor.callWhenRunning(init_world, config)
    internet.reactor.run()

def main():
    ''' parse arguments with .bin.cursed_lich_server '''
    from bin import cursed_lich_server
    cursed_lich_server()

if __name__ == '__main__':
    main()
