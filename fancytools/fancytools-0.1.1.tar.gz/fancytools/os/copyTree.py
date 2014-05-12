# -*- coding: utf-8 -*-
import os
import shutil

def copytree(src, dst, symlinks=False, ignore=None):
	'''
	copy one dir-tree into another
	combine dirs of the same name
	replacing files of same name
	'''
	if not os.path.exists(dst):
		os.makedirs(dst)
	for item in os.listdir(src):
		s = os.path.join(src, item)
		d = os.path.join(dst, item)
		if os.path.isdir(s):
			copytree(s, d, symlinks, ignore)
		else:
			if not os.path.exists(d) or os.stat(src).st_mtime - os.stat(dst).st_mtime > 1:
				shutil.copy2(s, d)