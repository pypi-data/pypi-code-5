#!/usr/bin/env python

from pyhi import HiData, maybe_pretty

import logging
import datetime

logging.basicConfig(level=logging.INFO)
log = logging.basicConfig(level=logging.INFO)

tzoffset = -7200

def dtstr(tstampms):
    t = tstampms/1000 + tzoffset
    return datetime.datetime.fromtimestamp(t)

def do_mytrades(uid, passwd):
    print '############ Open session: ############'
    mytrades = HiData(uid, passwd, instrument='AUDUSD', resolution='D1', automatonName='MyTradesAUDUSD', initialTime=1245803300000, baseurl='http://historicalinvestor.com')
    print 'Session:', mytrades._session
    print 'Token:', mytrades._token

    print '\n\n############ Get market data: ############'
    print '\n\nDATA acquired:', maybe_pretty(mytrades.get_data(1244248300000, 5))

    t = 1244248300000
    print '\n\n############ Market order, buy at {0}: ############'.format(dtstr(t))

    print '\n\nOrder:', maybe_pretty(mytrades.order(t, 1))

    t += 600*1000
    print '\n\n############ Market order, sell at {0}: ############'.format(dtstr(t))
    print '\n\nOrder:', maybe_pretty(mytrades.order(t, -1))

    print '\n\n############ Close session: ############'
    mytrades.finish()

    
if __name__ == '__main__':
    restid = 'id-*******'
    restpasswd = 'pass********'
    do_mytrades(restid, restpasswd)
