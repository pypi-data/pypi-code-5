# -*- coding: utf-8 -*-
from flask import flash
from lib.dict2xml import dict2xml


class ElGatoException(Exception):
    def __init__(self, code=None, message=None):
        Exception.__init__(self, message)
        self.code = code
    def __unicode__(self):
        return u"{} {}".format(self.code, self.message)

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Greška u polju (%s): %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')

def obj2tuple(obj):
    """
    Helper function, Embed obj as tuple if obj is not a list or tuple. Needed to process xml with one descendant node
    """
    if type(obj) in (tuple, list):
        return obj
    else:
        return [obj]

def row2dict(SA_object):
        return dict([(k, getattr(SA_object, k)) for k in SA_object.__dict__.keys() if not k.startswith("_")])



def xmlerror(errorcode = "", errortype = "", errortext = "", errorstack = ""):
    error = {"error": {"code": errorcode, "text": errortext, "stack": errorstack, "type": errortype}}
    return dict2xml(error)

def error_stack():
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if not exc is None:  # i.e. if an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if not exc is None:
         stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr

TAC_HTTP_ERROR_CODE=422
TAC_ERROR_CODE=1

def try_and_catch(f, http_error_code=TAC_HTTP_ERROR_CODE):
    """ Flask decorator for routes, catch exception and return xml error
    """
    from functools import wraps
    from flask import current_app, make_response, abort, Response
    import re

    try:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)

            except ElGatoException as e:
                etype = e.__class__.__name__
                xmlerr = xmlerror(errorcode=e.code,
                                  errortype=etype,
                                  errortext=e.message,
                                  errorstack=error_stack())
                current_app.logger.error(xmlerr)
                return Response(response=xmlerr, content_type='text/xml; charset=utf-8', status=http_error_code)
                #abort(make_response(xmlerr, http_error_code))

            except Exception as e:
                etype = e.__class__.__name__
                #etype = e.__module__ + "." + e.__class__.__name__
                xmlerr = xmlerror(errorcode="",
                                  errortype=etype,
                                  errortext=e.message,
                                  errorstack=error_stack())
                current_app.logger.error(xmlerr)
                return Response(response=xmlerr, content_type='text/xml; charset=utf-8', status=http_error_code)
                #abort(make_response(xmlerr, http_error_code))

        return decorated_function

    except ElGatoException as e:
        etype = e.__class__.__name__
        xmlerr = xmlerror(errorcode=e.code,
                          errortype=etype,
                          errortext=e.message,
                          errorstack=error_stack())
        current_app.logger.error(xmlerr)
        return Response(response=xmlerr, content_type='text/xml; charset=utf-8', status=http_error_code)
        #abort(make_response(xmlerr, http_error_code))

    except Exception as e:
        #etype = e.__module__ + "." + e.__class__.__name__
        etype = e.__class__.__name__
        xmlerr = xmlerror(errorcode="",
                          errortype=etype,
                          errortext=e.message,
                          errorstack=error_stack())
        current_app.logger.error(xmlerr)
        return Response(response=xmlerr, content_type='text/xml; charset=utf-8', status=http_error_code)
        #abort(make_response(xmlerr, http_error_code))

def returns_xml(f):
    """ Flask decorator for routes, return text/xml content
    """
    from functools import wraps
    from flask import Response
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        if type(r) == type(Response()):
            return r
        else:
            return Response(r, content_type='text/xml; charset=utf-8')
    return decorated_function

