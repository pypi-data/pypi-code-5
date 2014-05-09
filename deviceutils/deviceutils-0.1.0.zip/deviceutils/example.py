#!/usr/bin/env python
"""
"""
from .device import Device
from .io import SerialPort
from .io import TcpSocket
from .channel import channel
from .action import Query


def example_1(serial_port=0, tcp_host='localhost', tcp_port=5025):
    with channel(Device(), SerialPort(serial_port, timeout=6.0)) as dev:
        print(dev.stdio.closed)
        print(dev.stdio.io_min_delta)
        dev.stdio.io_min_delta = 3.0
        dev.send('Hello')
        print('Wrote ``Hello``.')
        dev.send('World!')
        print('Wrote ``World!``.')
        print('Attempting a read...')
        print(dev.receive(encoding=None))

    try:
        with channel(Device(), TcpSocket(tcp_host, tcp_port, timeout=10.0)) as dev:
            print(dev.stdio.closed)
            print(dev.receive(32).strip())
    except ConnectionRefusedError as e:
        print("TCP connection to {h!s}:{p!s} could not be established!\n{e!s}".format(
            h=tcp_host, p=tcp_port, e=e))


def example_2(tcp_host='localhost', tcp_port=5025):
    query0 = Query('Hello World!', device=Device(), io=TcpSocket(tcp_host, tcp_port, timeout=10.0))
    query0()
    print(query0.value)
