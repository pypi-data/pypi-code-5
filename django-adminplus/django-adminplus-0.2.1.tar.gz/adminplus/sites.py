from django.contrib.admin.sites import AdminSite
from django.utils.text import capfirst


class AdminPlusMixin(object):
    """Mixin for AdminSite to allow registering custom admin views."""

    index_template = 'adminplus/index.html'  # That was easy.

    def __init__(self, *args, **kwargs):
        self.custom_views = []
        return super(AdminPlusMixin, self).__init__(*args, **kwargs)

    def register_view(self, path, name=None, urlname=None, visible=True,
                      view=None):
        """Add a custom admin view. Can be used as a function or a decorator.

        * `path` is the path in the admin where the view will live, e.g.
            http://example.com/admin/somepath
        * `name` is an optional pretty name for the list of custom views. If
            empty, we'll guess based on view.__name__.
        * `urlname` is an optional parameter to be able to call the view with a
            redirect() or reverse()
        * `visible` is a boolean to set if the custom view should be visible in
            the admin dashboard or not.
        * `view` is any view function you can imagine.
        """
        if view is not None:
            self.custom_views.append((path, view, name, urlname, visible))
            return

        def decorator(fn):
            self.custom_views.append((path, fn, name, urlname, visible))
            return fn
        return decorator

    def get_urls(self):
        """Add our custom views to the admin urlconf."""
        urls = super(AdminPlusMixin, self).get_urls()
        from django.conf.urls import patterns, url
        for path, view, name, urlname, visible in self.custom_views:
            urls += patterns(
                '',
                url(r'^%s$' % path, self.admin_view(view), name=urlname),
            )
        return urls

    def index(self, request, extra_context=None):
        """Make sure our list of custom views is on the index page."""
        if not extra_context:
            extra_context = {}
        custom_list = []
        for path, view, name, urlname, visible in self.custom_views:
            if visible is True:
                if name:
                    custom_list.append((path, name))
                else:
                    custom_list.append((path, capfirst(view.__name__)))

        # Sort views alphabetically.
        custom_list.sort(key=lambda x: x[1])
        extra_context.update({
            'custom_list': custom_list
        })
        return super(AdminPlusMixin, self).index(request, extra_context)


class AdminSitePlus(AdminPlusMixin, AdminSite):
    """A Django AdminSite with the AdminPlusMixin to allow registering custom
    views not connected to models."""
