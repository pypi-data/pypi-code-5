from Acquisition import aq_inner
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from plonetheme.gov.browser.gov_folder_view import GovFolderView
from collective.contentleadimage.browser.viewlets import LeadImageViewlet

def tag(self, obj, css_class='tileImage'):
    context = aq_inner(obj)
    field = context.getField(IMAGE_FIELD_NAME)
    if field is not None:
        if field.get_size(context) != 0:
            scale = self.prefs.desc_scale_name
            try:
                return field.tag(context, scale=scale, css_class=css_class)
            except:
                return ''
    return ''

GovFolderView.tag = tag


# We patch the render of the leadimage viewlet to also show it for News Items
# the .pt is also overridden
def render(self):
    context = aq_inner(self.context)
    portal_type = getattr(context, 'portal_type', None)
    allowed_types = list(self.prefs.allowed_types)
    allowed_types.append('News Item')
    if portal_type in allowed_types:
        return super(LeadImageViewlet, self).render()
    else:
        return ''

LeadImageViewlet.render = render
