#!/usr/bin/env python2

import argparse

parser = argparse.ArgumentParser(description='List all parts used in a .craft file')
parser.add_argument('craft', type=str, help='Path to the .craft file')
args = parser.parse_args()

parts = set()
with open(args.craft, 'r') as f:
    for line in f.readlines():
        if 'part = ' in line:
            part = line.split(' = ')[1].split('_')[0]
            parts.add(part)

for part in sorted(parts):
    print part
