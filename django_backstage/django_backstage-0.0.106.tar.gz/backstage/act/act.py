import os
import sys
import tarfile
import tempfile
import backstage
from backstage.venue import use_venue
from backstage.venue import Venue

class Act():
    def __init__(self, venue, actname):
        self.venue = venue
        self.actname = actname
        self.acthome = os.path.join(self.venue.VENUE_ROOT, 'acts', actname)
        self.uwsgifile = os.path.join(self.acthome, 'uwsgi.ini')
        if not os.path.exists(self.acthome):
            print 'Act %s does not exist in venue %s' % (self.venue.VENUE_NAME, self.actname)
            raise
        self.get_settings()

    def get_settings(self):
        syspath = sys.path
        sys.path.insert(0,os.path.join(self.venue.VENUE_ROOT,'acts'))
        exec('from %s import settings' % self.actname)
        sys.path = syspath
        self.settings = settings

    def uwsgi_linker(self, linkmode='link'):
        linkmodes = ['link', 'unlink', 'relink']
        inifile = os.path.abspath(os.path.join(self.acthome, 'uwsgi.ini'))
        linkfile = self.settings.UWSGI_VASSALS
        if linkmode not in linkmodes:
            return 'Usage: uwsgi_linker <%s>' % (linkmodes)
        if linkmode == 'link':
            pass
        elif linkmode == 'unlink':
            pass
        elif linkmode == 'relink':
            pass

def new_act(venue, actname):
    """create a new Act within a backstage Venue"""
    if isinstance(venue, str):
        try:
            venue = use_venue(venue)
        except:
            venue = None
    if not isinstance(venue, Venue):
        print '%s is not a valid backstage venue' % (venue)
        return None
    actsdir = os.path.join(venue.VENUE_ROOT, 'acts')
    acthome = os.path.join(actsdir, actname)
    if os.path.exists(acthome):
        print 'A folder named %s already exists under %s' % (actname, actsdir)
        return None
    os.mkdir(acthome)
    copy_act_skel(venue, actsdir, actname)
    create_act_uwsgi_file(venue, actsdir, actname)

    act = Act(venue, actname)
    if act:
        s = 'created Backstage Act %s at %s' % (actname, acthome)
        print s
        s = 'using Act %s' % (act)
        print s
    return act

def create_act_uwsgi_file(venue, actsdir, actname):
    """create the uwsgi ini file for a (usually) new Act. This reads in backstage/conf/uwsgi.ini.src
    and substitutes values appropriately."""
    srcfile = os.path.join(os.path.dirname(backstage.__file__),'conf/uwsgi.ini.src')
    with open(srcfile,'r') as f:
        srcdata = f.read()
    outfile = os.path.join(actsdir, actname, 'uwsgi.ini')
    o = open(outfile,'w')
    o.write(srcdata.format(VENUE_ROOT=venue.VENUE_ROOT, VENUE_NAME=venue.VENUE_NAME, ACT_NAME=actname))
    o.close()
    return

def copy_act_skel(venue, actsdir, actname):
    """copy the skeleton files into the Act instance folder"""
    backstage_home = os.path.dirname(os.path.abspath(backstage.__file__))
    act_home = os.path.join(actsdir, actname)
    act_skel = os.path.join(backstage_home,'skel/act')
    #recursive copy via tar
    tmpfile = tempfile.NamedTemporaryFile()
    tmpfile.close()
    tar_file = tarfile.open(tmpfile.name,'w')
    cwd = os.getcwd()
    os.chdir(act_skel)
    tar_file.add('.')
    os.chdir(cwd)
    tar_file.close()
    tar_file = tarfile.open(tmpfile.name,'r')
    tar_file.extractall(act_home)
    tar_file.close()
    os.remove(tmpfile.name)
