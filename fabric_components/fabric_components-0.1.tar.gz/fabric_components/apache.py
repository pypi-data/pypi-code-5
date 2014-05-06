from fabric.api import *

def install_apache(mods=[], disable_mods=[], disable_sites=[]):
    sudo("apt-get -q -y install apache2 libapache2-mod-wsgi")
    for mod in mods:
        sudo("a2enmod %s" % mod)

    for site in disable_sites:
        sudo("a2dissite %s" % site)
