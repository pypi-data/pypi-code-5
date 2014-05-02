"""Initialize the database with data for the Rank model.

The database must be empty otherwise an Integrity error will be raised. The
table is not cleared first in case the script is run inadvertently on an
existing database.
"""
from checklists import get_data_path
from checklists.models import Rank, set_current_user, clear_current_user
from checklists.utils import i18n_fieldnames

from utils import create_objects, get_data


def run():
    set_current_user('load_ranks')
    fields = ('id', 'slug') + i18n_fieldnames('name')
    data = get_data(get_data_path('rank.csv'))
    create_objects(Rank, fields, data)
    clear_current_user()
