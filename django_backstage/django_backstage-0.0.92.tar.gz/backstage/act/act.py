import os
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
            a = new_act(venue, actname)
        if not os.path.exists(self.uwsgifile):
            self.create_act_uwsgi_file()

    def create_act_uwsgi_file(self):
        """create the uwsgi ini file for a (usually) new Act. This reads in backstage/conf/uwsgi.ini.src
        and substitutes values appropriately."""
        srcfile = os.path.join(os.path.dirname(backstage.__file__),'conf/uwsgi.ini.src')
        with open(srcfile,'r') as f:
            srcdata = f.read()
        outfile = os.path.join(self.acthome,'uwsgi.ini')
        o = open(outfile,'w')
        o.write(srcdata.format(VENUE_ROOT=self.venue.VENUE_ROOT,VENUE_NAME=self.venue.VENUE_NAME,ACT_NAME=self.actname))
        o.close()

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
    acts_dir = os.path.join(venue.VENUE_ROOT, 'acts')
    act_home = os.path.join(acts_dir, actname)
    if os.path.exists(act_home):
        print 'A folder named %s already exists under %s' % (actname, acts_dir)
        return None
    os.mkdir(act_home)

    a = Act(venue, actname)
    return a

