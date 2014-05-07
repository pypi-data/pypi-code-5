# -*- coding: utf-8 -*-

import logging

try:
    from Products.ATContentTypes.content.file import ATFileSchema
except ImportError:
    ATFileSchema = None

try:
    from plone.app.blob.subtypes.file import SchemaExtender as FileSchemaExtender
except ImportError:
    FileSchemaExtender = None

logger = logging.getLogger('rt.filenotindexed')

if ATFileSchema:
    ATFileSchema['file'].searchable = False
    logger.warning('Disabled indexing of ATFile')
if FileSchemaExtender:
    FileSchemaExtender.fields[0].searchable = False
    logger.warning('Disabled indexing of ATBlob')

