"""bootstrap implementation of base templates

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
# XXX Backport from squareui

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb.utils import UStringIO
from cubicweb.web.views import basetemplates


HTML5 = u'<!DOCTYPE html>'

basetemplates.TheMainTemplate.doctype = HTML5


###############################################################################
### GLOBAL CALL ###############################################################
###############################################################################
@monkeypatch(basetemplates.TheMainTemplate)
def call(self, view):
    self.set_request_content_type()
    self.template_header(self.content_type, view)
    w = self.w
    w(u'<div class="row-fluid">')
    w(u'<div class="span12" id="pageContent">')
    vtitle = self._cw.form.get('vtitle')
    if vtitle:
        w(u'<div class="vtitle">%s</div>\n' % xml_escape(vtitle))
    # display entity type restriction component
    etypefilter = self._cw.vreg['components'].select_or_none(
        'etypenavigation', self._cw, rset=self.cw_rset)
    if etypefilter and etypefilter.cw_propval('visible'):
        etypefilter.render(w=w)
    nav_html = UStringIO()
    if view and not view.handle_pagination:
        view.paginate(w=nav_html.write)
    w(nav_html.getvalue())
    w(u'<div id="contentmain">\n')
    view.render(w=w)
    w(u'</div>\n') # closes id=contentmain
    w(nav_html.getvalue())
    w(u'</div>\n' # closes id=pageContent
      u'</div>\n') # closes row-fluid
    self.template_footer(view)


###############################################################################
### NAV COLUMN AND TOOLBAR ####################################################
###############################################################################
@monkeypatch(basetemplates.TheMainTemplate)
def nav_toolbar(self, view):
    boxes = list(self._cw.vreg['ctxcomponents'].poss_visible_objects(
        self._cw, rset=self.cw_rset, view=view, context='nav-toolbar'))
    if boxes:
        for box in boxes:
            box.render(w=self.w, view=view)

@monkeypatch(basetemplates.TheMainTemplate)
def nav_column(self, view, context):
    boxes = list(self._cw.vreg['ctxcomponents'].poss_visible_objects(
        self._cw, rset=self.cw_rset, view=view, context=context))
    if boxes:
        getlayout = self._cw.vreg['components'].select
        self.w(u'<div id="aside-main-%s" class="span3">\n' % context)
        self.w(u'<div class="navboxes" id="navColumn%s">\n' % context.capitalize())
        for box in boxes:
            box.render(w=self.w, view=view)
        self.w(u'</div></div>')
    return len(boxes)


###############################################################################
### HEADER ####################################################################
###############################################################################
@monkeypatch(basetemplates.TheMainTemplate)
def template_html_header(self, content_type, page_title,
                         additional_headers=()):
    w = self.whead
    lang = self._cw.lang
    self.write_doctype()
    # explicitly close the <base> tag to avoid IE 6 bugs while browsing the DOM
    self._cw.html_headers.define_var('BASE_URL', self._cw.base_url())
    self._cw.html_headers.define_var('DATA_URL', self._cw.datadir_url)
    w(u'<meta http-equiv="content-type" content="%s; charset=%s"/>\n'
      % (content_type, self._cw.encoding))
    w(u'<meta name="viewport" content="initial-scale=1.0; '
      u'maximum-scale=1.0; width=device-width; "/>')
    w(u'\n'.join(additional_headers) + u'\n')
    # FIXME this is a quick option to make cw work in IE9
    # you'll lose all IE9 functionality, the browser will act as IE8.
    w(u'<meta http-equiv="X-UA-Compatible" content="IE=8" />\n')
    w(u'<!-- Le HTML5 shim, for IE6-8 support of HTML elements -->\n'
      u'  <!--[if lt IE 9]>\n'
      u'        <script src="%s"></script>\n'
      u'  <![endif]-->\n' % self._cw.data_url('js/html5.js'))
    self.wview('htmlheader', rset=self.cw_rset)
    if page_title:
        w(u'<title>%s</title>\n' % xml_escape(page_title))

@monkeypatch(basetemplates.TheMainTemplate)
def template_body_header(self, view):
    w = self.w
    w(u'<body>\n')
    self.wview('header', rset=self.cw_rset, view=view)
    # Toolbar
    w(u'<div id="toolbar" class="container-fluid">\n'
      u'<div class="row-fluid offset3">\n')
    self.nav_toolbar(view)
    w(u'</div></div>\n')
    # Page
    w(u'<div id="page" class="container-fluid">\n'
      u'<div class="row-fluid">\n')
    #w(u'<div class="span3">')
    nb_boxes = self.nav_column(view, 'left')
    #w(u'</div>')
    if nb_boxes is not None and nb_boxes:
        content_span = 9
    else:
        content_span = 12
    w(u'<div id="contentColumn" class="span%s">' % content_span)
    components = self._cw.vreg['components']
    rqlcomp = components.select_or_none('rqlinput', self._cw, rset=self.cw_rset)
    if rqlcomp:
        rqlcomp.render(w=self.w, view=view)
    msgcomp = components.select_or_none('applmessages', self._cw, rset=self.cw_rset)
    if msgcomp:
        msgcomp.render(w=self.w)
    self.content_header(view)

@monkeypatch(basetemplates.HTMLPageHeader)
def main_header(self, view):
    """build the top menu with authentification info and the rql box"""
    spans = {'headtext': 3,
             'header-center': 7,
             'header-right': 2,
             }
    w = self.w
    w(u'<div id="header" class="navbar">'
      u'<div class="navbar-inner">'
      u'<div class="container">'
      u'<div class="row-fluid">')
    prev_span_size = 0
    for colid, context in self.headers:
        components = self._cw.vreg['ctxcomponents'].poss_visible_objects(
            self._cw, rset=self.cw_rset, view=view, context=context)
        if components:
            span_size = spans.get(colid, 2) + prev_span_size
            prev_span_size = 0
            w(u'<div id="%s" class="span%s">' % (colid, span_size))
            klass = ' pull-right' if context in ('header-center', 'header-right') else ''
            w(u'<ul class="nav%s">' % klass)
            for comp in components:
                w(u'<li>')
                comp.render(w=w)
                w(u'</li>')
            w(u'</ul>')
            w(u'</div>')
        else:
            # Keep size to make a bigger span the next time
            prev_span_size += spans.get(colid, 2)
    w(u'</div></div></div></div>\n')
    # get login form to display it as modal window / Backport from Orbui
    login = self._cw.vreg['forms'].select_or_none('logform', self._cw)
    if login:
        self.w(u'<div id="loginModal" class="modal hide fade in">'
               u'<div class="modal-header">'
               u'<a class="close" data-dismiss="modal">x</a>'
               u'<h3>%s</h3>'
               u'</div>'
               u'<div class="modal-body">' % self._cw._('log in'))
        login.render(w=self.w)
    self.w(u'</div>'
           u' <div class="modal-footer"></div>'
           u'</div>')



###############################################################################
### FOOTER ####################################################################
###############################################################################
@monkeypatch(basetemplates.TheMainTemplate)
def template_footer(self, view=None):
    self.w(u'<div class="row">')
    self.content_footer(view)
    self.w(u'</div>')
    self.w(u'</div>\n') # XXX closes div#contentColumn span9 in template_body_header
    self.nav_column(view, 'right')
    self.w(u'</div>\n') # XXX closes div#page in template_body_header
    self.wview('footer', rset=self.cw_rset)
    self.w(u'</div>'    # closes class="row-fluid"
           u'</div>')   # closes class="container-fluid"
    self.w(u'</body>')


@monkeypatch(basetemplates.HTMLPageFooter)
def call(self, **kwargs):
    self.w(u'<footer id="pagefooter">')
    self.w(u'<div id="footer" class"container">')
    self.footer_content()
    self.w(u'</div>')
    self.w(u'</footer>')
