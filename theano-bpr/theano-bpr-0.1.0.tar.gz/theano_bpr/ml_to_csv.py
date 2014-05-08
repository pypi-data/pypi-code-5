#!/usr/bin/env python

import sys

ml_data = sys.argv[1]
threshold = int(sys.argv[2])

with open(ml_data) as f:
    for line in f.readlines():
        user, item, rating, ts = line.split('\t')
        if rating > threshold:
            print "%s,%s" % (user, item)
