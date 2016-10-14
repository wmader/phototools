#!/usr/bin/python

import os
import argparse
import itempack as ip
import packmanager as pm


parser = argparse.ArgumentParser(description="Move and rename my pictures.")
parser.add_argument('-r', '--raw',
                    action='store',
                    default='./',
                    help='Folder of raw files')
parser.add_argument('-j', '--jpg',
                    action='store',
                    default='jpg',
                    help='Folder of jpg files relative to raw files')
parser.add_argument('-d', '--dry',
                    action='store_true',
                    help='Show source and taget file names, but to not alter files.')

args = parser.parse_args()


manager = pm.PackManager(args.raw, jpgFolder=os.path.join(args.raw, args.jpg))
manager.process(args.dry)


