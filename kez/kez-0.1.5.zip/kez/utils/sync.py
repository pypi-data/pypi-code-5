#coding=utf-8
"""
Synchronize two directories.

Source: https://gist.github.com/xalexchen/7038205
"""
# This is a small python script to help you synchronize two folders
# Compatible with Python 2.x and Python 3.x

import filecmp, shutil, os, sys
 
IGNORE = ['.git', '.hg']
 
__all__ = [
    'syncfiles',
]

def get_cmp_paths(dir_cmp, filenames):
    return ((os.path.join(dir_cmp.left, f), os.path.join(dir_cmp.right, f)) for f in filenames)
 
def sync(dir_cmp):
    for f_left, f_right in get_cmp_paths(dir_cmp, dir_cmp.right_only):
        if os.path.isfile(f_right):
            os.remove(f_right)
        else:
            shutil.rmtree(f_right)
        print('delete %s' % f_right)  
    for f_left, f_right in get_cmp_paths(dir_cmp, dir_cmp.left_only+dir_cmp.diff_files):
        if os.path.isfile(f_left):
            shutil.copy2(f_left, f_right)
        else:
            shutil.copytree(f_left, f_right)
        print('copy %s' % f_left)
    for sub_cmp_dir in dir_cmp.subdirs.values():
        sync(sub_cmp_dir)
 
def syncfiles(src, dest, ignore=IGNORE):
    if not os.path.exists(src):
        print('= =b Please check the source directory was exist')
        print('- -b Sync file failure !!!')
        return
    if os.path.isfile(src):
        print('#_# We only support for sync directory but not a single file,one file please do it by yourself')
        print('- -b Sync file failure !!!')
        return
    if not os.path.exists(dest):
        os.makedirs(dest)    
    dir_cmp = filecmp.dircmp(src, dest, ignore=IGNORE)
    sync(dir_cmp)
    print('^_^ Sync file finished!')
 
