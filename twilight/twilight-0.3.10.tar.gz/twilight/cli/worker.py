import os
import bz2
import json
import socket
import redis
import time
from twilight.lib import geo, tweets


import logging
logger = logging.getLogger(__name__)


def ns(*parts):
    return ':'.join(['twilight'] + list(parts))


def geocode(payload, host, shapefile=None):
    '''
    `task` should look like this:
    {
        "method": "geocode"
        "input": "/mnt/mark1/twitter/nafrica_2013-05-13T06-59-00.ttv2.bz2",
        "output": "/mnt/mark1/worker/nafrica_2013-05-13T06-59-00.tsv",
    }
    '''
    # we keep the original payload around since we need the exact payload in order to remove it when we're done
    task = json.loads(payload)
    if shapefile is None:
        # ESRI Shapefile filepath
        shapefile = os.path.expanduser('~/corpora/TM_WORLD_BORDERS-0.3/TM_WORLD_BORDERS-0.3.shp')
    countries = geo.AreaCollection.from_tm_world_borders_shapefile(shapefile)

    resolved = 0
    total = 0
    started = time.time()
    with open(task['output'], 'w') as output_fd:
        with bz2.BZ2File(task['input'], 'r') as input_fd:
            for line in input_fd:
                tweet = tweets.TTV2.from_line(line)

                total += 1
                location = ''
                # location may be empty if the tweet has no coordinates or if they don't correspond to a country in our map
                if tweet.coordinates != '':
                    lon, lat = map(float, tweet.coordinates.split(','))
                    country = countries.first_area_containing(lon, lat)
                    if country:
                        location = unicode(country.name)
                        resolved += 1

                # this print should handle the
                print >> output_fd, location.encode('utf8')

    task.update(
        elapsed=int(time.time() - started),
        resolved=resolved,
        total=total
    )

    # success! move this job over to the "done" list
    r = redis.StrictRedis(host=host)
    # -1 means: remove at most the rightmost 1 of these from the "incomplete" list
    # (there shouldn't be anything other than 1, but just in case, should help debugging)
    r.lrem(ns('worker', 'incomplete'), payload, -1)
    r.lpush(ns('worker', 'done'), json.dumps(task))

    logger.info('finished with task: %s', payload)


def main(parser):
    parser.add_argument('--host', type=str,
        help='Hostname of current machine',
        default=socket.gethostname())
    parser.add_argument('--cc', type=str,
        help='Redis database address',
        default='salt')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Log extra information')
    opts = parser.parse_args()

    level = logging.DEBUG if opts.verbose else logging.INFO
    logging.basicConfig(level=level)

    r = redis.StrictRedis(host=opts.cc)
    methods = dict(geocode=geocode)
    try:
        pop = ns('worker', 'queue')
        push = ns('worker', 'incomplete')
        while True:
            logger.info('BRPOPLPUSH %s %s', pop, push)
            payload = r.brpoplpush(pop, push, timeout=0)
            logger.info('got payload: %s', payload)
            task = json.loads(payload)
            methods[task['method']](payload, host=opts.cc)
    except (KeyboardInterrupt, SystemExit), exc:
        logger.critical('exiting: %r' % exc)
