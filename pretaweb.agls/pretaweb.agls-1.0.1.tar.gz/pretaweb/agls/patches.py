from DateTime import DateTime

# we patch this method to ensure creation date takes into account
# client's timezone on setting new date input from user
def setCreationDate(self, creation_date=None):
    """Set the date when the resource was created.
    When called without an argument, sets the date to now.
    """
    created = creation_date
    if not created:
        created = DateTime()
    self.getField('creation_date').set(self, created)

from Products.Archetypes.ExtensibleMetadata import ExtensibleMetadata
ExtensibleMetadata._orig_setCreationDate = ExtensibleMetadata.setCreationDate
ExtensibleMetadata.setCreationDate = setCreationDate
