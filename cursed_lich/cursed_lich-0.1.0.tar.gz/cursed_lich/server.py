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
from error import (PermissionError, HeroExistsError, CellOccupiedError, 
    NoCellError)

__version__ = 1

LOG = None

def get_sessions_user(sesh, session_id):
    ''' Check to see if session is valid for request '''
    session = sesh.query(db.Session).filter_by(
        request_session_id=session_id).first()
    if session is None:
        LOG.warning('received request with invalid session id')
        return None
    return session.user

def invalid_user_request(sesh, user, req):
    ''' Need to check if the request is for a hero owned by the user '''
    if user is None:
        return True
    if req.typ == net_pb2.MT_INFO_HERO:
        return False
    elif req.typ == net_pb2.MT_CREATE_HERO:
        return False
    elif req.typ == net_pb2.MT_ACTION:
        hero = sesh.query(db.Hero).filter_by(
            name=req.action_request.name).first()
        return hero.user != user
    return False

def retry(func, args, kwargs, error_class, retries=20):
    ''' Retries and catches a certain error, re-raising if it still fails ''' 
    times = 0
    while times < retries:
        try:
            ret = func(*args, **kwargs)
            break
        except error_class:
            times += 1
    else:
        raise error_class('retried %d times, still failed' % retries)
    return ret

class LichProtocol(internet.protocol.Protocol):
    ''' Servz '''

    def __init__(self, factory, addr):
        ''' Set up the basics '''
        self.factory = factory
        self.addr = addr
        self.logger = self.factory.logger
        self.db = self.factory.db
        self.config = self.factory.config

    def init_response(self, req):
        ''' Create the start to the response '''
        res = net_pb2.Response()
        res.response_id = req.request_id
        res.version = __version__
        res.compatible = True
        res.typ = req.typ
        # default is success
        res.status = net_pb2.SC_SUCCESS
        return res

    def check_permission(self, req, res):
        ''' See if it's a good session, and that user can do what they're
        trying to do (they own the hero) 
        '''
        user = get_sessions_user(self.db, req.session_id)
        if invalid_user_request(self.db, user, req):
            res.status = net_pb2.SC_INVALID_SESSION
            res.error = 'Invalid Session ID (expired or just bad)'
            self.transport.write(res.SerializeToString())
            self.logger.error('IP(%s) caused PermissionError' % self.addr)
            raise PermissionError('IP(%s)' % self.addr)
        return user

    def login_request(self, req, res):
        ''' build response for a login request '''
        user = self.db.query(db.User).filter_by(
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
            sid = db.create_request_session(self.db, user)
            res.login_response.session_id = sid

    def create_hero_request(self, req, res, user):
        ''' build response for a hero creation request '''
        # Defined in server's customizable config file
        tries = 0
        while tries < 50:
            pos = self.config.starting_pos()
            try:
                db.add_hero(user.username, req.create_hero_request.name, pos)
            except HeroExistsError:
                self.logger.warning("IP(%s) tried to create hero %s but it "
                    "already exists." % (self.addr, req.create_hero_request.name))
                res.status = net_pb2.SC_NON_UNIQUE_HERO_NAME
                res.error = 'Hero name already exists.'
            except NoCellError:
                self.logger.error("config's STARTING_RECTS are not in good range")
                self.logger.error("Couldn't create hero at %s" % pos)
                res.status = net_pb2.SC_SERVER_MISCONFIGURATION
                res.error = 'Server misconfigured. Could not create hero.'
            except CellOccupiedError:
                self.logger.warning('hero cannot spawn. occupied @ %s' % pos)
                # Retry for a bit
                tries += 1
                continue
            break
        res.create_hero_response.success = True

    def dataReceived(self, data):
        ''' Receive raw data '''
        req = net_pb2.Request()
        try:
            req.ParseFromString(data)
        except DecodeError:
            self.logger.error(
                'server could not decode data from request: %s' 
                % data.encode('hex'))
            raise
        res = self.init_response(req)
        # non login attempts need valid session id
        if req.typ != net_pb2.MT_LOGIN:
            # raises PermissionError
            user = self.check_permission(req, res)
        # login attempt
        if req.typ == net_pb2.MT_LOGIN:
            self.login_request(req, res)
        # get info on heroes
        elif req.typ == net_pb2.MT_INFO_HERO:
            pass
        # create a new hero
        elif req.typ == net_pb2.MT_CREATE_HERO:
            self.create_hero_request(req, res, user)
        # perform an action, like move a hero
        elif req.typ == net_pb2.MT_ACTION:
            pass
        # Malformed request or non compatible versions
        else:
            res.status = net_pb2.SC_INVALID_REQUEST_TYPE
        self.transport.write(res.SerializeToString())

class LichFactory(internet.protocol.Factory):
    
    def __init__(self, config):
        self.config = config
        self.logger = config.logger
        self.db = config.sesh

    def buildProtocol(self, addr):
        return LichProtocol(self, addr)

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
    if config.sesh.query(db.Cell).count() < config.WIDTH * config.HEIGHT:
        init_map(config)
    config.logger.info('DB map populated.')

def init_server(config):
    ''' Initialize listener '''
    # I feel dirty, but this is just going to happen anyway.
    config.logger.debug('Initializing server.')
    if run_init_checks(config):
        config.logger.error('Please fix errors and restart.')
        return

    global LOG
    LOG = config.logger

    lich_factory = LichFactory(config)
    lich_factory.protocol = LichProtocol
    if config.USE_SSL:
        internet.reactor.listenSSL(config.SERVER_PORT, lich_factory,
            internet.ssl.DefaultOpenSSLContextFactory(
            config.SSL_KEY_PATH,
            config.SSL_CERT_PATH))
    else:
        internet.reactor.listenTCP(config.SERVER_PORT, lich_factory)
    internet.reactor.callWhenRunning(init_world, config)
    internet.reactor.run()

def main():
    ''' parse arguments with .bin.cursed_lich_server '''
    from bin import cursed_lich_server
    cursed_lich_server()

if __name__ == '__main__':
    main()
