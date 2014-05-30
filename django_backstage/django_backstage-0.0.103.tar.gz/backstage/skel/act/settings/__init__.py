import os
import sys
settings_path = os.path.dirname(os.path.abspath(__file__))
act_path = os.path.dirname(settings_path)
acts_home, act_name = os.path.split(act_path)
venue_path = os.path.dirname(acts_home)
venue_parent, venue_name = os.path.split(venue_path)
sys.path.insert(0,venue_parent)
exec('from %s.settings import *' % venue_name)
sys.path.insert(0,acts_home)
ROOT_URLCONF = '%s.acts.%s.urls' % (venue_name, act_name)
INSTALLED_APPS.insert(0,'%s.acts.%s' % (venue_name, act_name))