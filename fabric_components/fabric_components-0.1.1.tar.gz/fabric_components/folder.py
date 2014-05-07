from fabric.api import *


def create_folder(path, owner=None, group=None, mod=None):
    """
    create_folder(path, owner, group, mod) creates the folder and set owner, group, mod on it
    """
    sudo('mkdir -p %s' % path)

    if owner:
        sudo('chown %s %s' % (owner, path))

    if group:
        sudo('chgrp %s %s' % (group, path))

    if mod:
        sudo('chmod %s %s' % (mod, path))