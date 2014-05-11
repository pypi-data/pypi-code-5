#!/usr/bin/env python
import argparse
from client import JenkinsClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("address", type=str,
                        help="Full address of the build server including port number.")
    parser.add_argument("-i", "--interval", type=int,
                        help="Set the polling interval in seconds. Default is 300.")
    parser.add_argument('-j', '--jobs', nargs='+', type=str,
                        help="Names of jenkins jobs to monitor for changes.")
    args = parser.parse_args()

    j = JenkinsClient(address=args.address, build_names=args.jobs,
                      polling_interval=args.interval)
    j.run()
