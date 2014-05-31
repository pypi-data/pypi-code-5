#!/usr/bin/env python

from twisted import internet
import twisted.internet.protocol
import twisted.internet.reactor
import twisted.internet.ssl

import db
import terrain

class CursedLichServer(internet.protocol.Protocol):
    def dataReceived(self, data):
        ''' Echo server as an example twisted project '''
        self.transport.write(data)

def init_map(sesh, config):
    ''' Set up Cells in DB '''
    print('DB not populated with Terrain. Populating...')
    cells = terrain.Terrain.create_terrain(
        config.WIDTH, config.HEIGHT, config.Z_Level.MIDGAARD)
    print('Completed creating map. Writing to DB...')
    sesh.add_all(cells)
    sesh.commit()

def init_backend(config):
    ''' Set up and save database session '''
    config.get_session = db.create_session(config.DB_PATH)
    config.session = config.get_session()
    sesh = config.session
    if sesh.query(db.Cell).count() < config.WIDTH * config.HEIGHT:
        init_map(sesh, config)
    print('DB map populated.')

def init_server(config):
    ''' Initialize listener '''
    factory = internet.protocol.Factory()
    factory.protocol = CursedLichServer
    if config.USE_SSL:
        internet.reactor.listenSSL(config.SERVER_PORT, factory,
            internet.ssl.DefaultOpenSSLContextFactory(
            config.SSL_KEY_PATH,
            config.SSL_CERT_PATH))
    else:
        internet.reactor.listenTCP(config.SERVER_PORT, factory)
    internet.reactor.callWhenRunning(init_backend, config)
    internet.reactor.run()

def main():
    ''' parse arguments with .bin.cursed_lich_server '''
    from bin import cursed_lich_server
    cursed_lich_server()

if __name__ == '__main__':
    main()
