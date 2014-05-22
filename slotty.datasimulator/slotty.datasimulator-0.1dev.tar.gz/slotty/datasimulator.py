import zmq.green as zmq
import random
import gevent
from operator import itemgetter

import logging

logger = logging.getLogger(__name__)

def poll_sensor(address):
    """ Simulate polling a Carrera Control Unit

    The public api for race timers right now is
    and will be sent as json string
    data = {'time': lap_time,
            'id': controller,
            'fastest': fastest,
            'laps': laps[controller],
            'fuel': fuel,
            'previous': previous}
    Subject to be change!
    """
    fastest_laps = {i: 999.0 for i in range(1, 7)}
    laps = {i: 0 for i in range(1, 7)}
    lap_time_estimate = 6.500
    variation = 0.500

    def read():
        """ Simulate some sensor, that can push"""
        lap_time = random.uniform(lap_time_estimate,
                                  lap_time_estimate + 0.100)
        data_list = []
        for controller in range(1, 7):
            laps[controller] += 1
            fastest = fastest_laps[controller]
            data = {'time': lap_time,
                    'id': controller,
                    'fastest': fastest,
                    'laps': laps[controller],
                    'fuel': '100',
                    'previous': None}
            offset = random.uniform(-variation, variation)
            if lap_time < fastest:
                data["time"] = lap_time
                data["fastest"] = lap_time
                fastest_laps[controller] = lap_time
            data_list.append(data)
            lap_time += offset

        gevent.sleep(lap_time)
        for i in sorted(data_list, key=itemgetter('time')):
            gevent.sleep(i['time'] - lap_time)
            yield i

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(address)
    logger.info("Binding to {0}".format(address))
    while True:
        for race_data in read():
            payload = {"event": "lap",
                       "args": race_data}
            logger.debug(payload)
            socket.send_json(payload)


if __name__ == "__main__":
    gevent.joinall([
        gevent.spawn(poll_sensor, "tcp://127.0.0.1:5000")])
