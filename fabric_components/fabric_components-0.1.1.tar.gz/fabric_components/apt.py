from fabric.api import *


def apt_get(*packages):
    sudo('apt-get -y --no-upgrade install %s' % ' '.join(packages))
