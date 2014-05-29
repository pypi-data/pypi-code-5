import os
from backstage.venue import use_venue
from backstage.venue import Venue

class Act():
    def __init__(self, venue, actname):
        self.venue = venue
        self.actname = actname
        pass
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
    acts_dir = os.path.join(venue.VENUE_ROOT, 'acts')
    act_home = os.path.join(acts_dir, actname)
    if os.path.exists(act_home):
        print 'A folder named %s already exists under %s' % (actname, acts_dir)
        return None
    os.mkdir(act_home)
    a = Act(venue, actname)
    return a

