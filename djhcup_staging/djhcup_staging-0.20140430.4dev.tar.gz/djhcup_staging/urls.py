# Django imports
from django.conf.urls import patterns, include, url


# local imports
import utils


# base patterns always available through having djhcup_core installed
urlpatterns = patterns('djhcup_staging',
                       
    # take this one out when done with it
    url(r'shovel_all/$', 'views.shovel_all_core_source', name='shovel_all_core_source'),
    
    url(r'files/discover/$', 'views.file_discover', name='file_discover'),
    url(r'files/match/$', 'views.file_match', name='file_match'),
    url(r'files/$', 'views.file_inventory', name='file_inventory'),

    url(r'sources/?$', 'views.source_inventory', name='source_inventory'),
    url(r'sources/defaults/?$', 'views.source_populate_defaults', name='source_populate_defaults'),
    url(r'sources/(?P<source_id>\d+)/$', 'views.source_detail', name='source_detail'),
    url(r'sources/(?P<source_id>\d+)/master/$', 'views.src_gen_master_table', name='src_gen_master_table'),
    
    url(r'batches/$', 'views.batch_inventory', name='batch_inventory'),
    url(r'batches/(?P<batch_id>\d+)/$', 'views.batch_detail', name='batch_detail'),
    url(r'batches/reset/$', 'views.batch_reset_dead', name='batch_reset_dead'),
    url(r'batches/import/(?P<batch_id>\d+)/?$', 'views.batch_import', name='batch_import'),
    url(r'batches/stage/(?P<batch_id>\d+)/?$', 'views.batch_stage', name='batch_stage'),
    url(r'$', 'views.index', name='index'),
)
