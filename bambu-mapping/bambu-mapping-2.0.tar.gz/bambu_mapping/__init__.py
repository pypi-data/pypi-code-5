from django.conf import settings

__version__ = '2.0'
PROVIDER = getattr(settings, 'MAPPING_PROVIDER',
    'bambu_mapping.providers.OpenStreetMapProvider'
)