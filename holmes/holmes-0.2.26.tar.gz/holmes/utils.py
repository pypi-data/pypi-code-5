#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from six.moves.urllib.parse import urlparse

EMPTY_DOMAIN_RESULT = ('', '')


def get_domain_from_url(url, default_scheme='http'):
    if not url:
        return EMPTY_DOMAIN_RESULT

    scheme = default_scheme
    result = urlparse(url)
    domain = result.netloc

    if (result.scheme and result.scheme in ['http', 'https']):
        scheme = result.scheme

    if (result.scheme and result.scheme not in ['http', 'https']) and not domain:
        domain = result.scheme
    else:
        if not domain:
            domain = result.path.split('/')[0]
            if not '.' in domain:
                return EMPTY_DOMAIN_RESULT

        if ':' in domain:
            domain = domain.split(':')[0]

    original_domain = domain.strip()
    domain = original_domain.replace('www.', '')

    return domain, '%s://%s/' % (scheme, original_domain)


def get_class(klass):
    module_name, class_name = klass.rsplit('.', 1)

    module = __import__(module_name)

    if '.' in module_name:
        module = reduce(getattr, module_name.split('.')[1:], module)

    return getattr(module, class_name)


def load_classes(classes=None, classes_to_load=None, default=None):
    if classes_to_load is None:
        classes_to_load = default

    if classes is None:
        classes = []

    for class_full_name in classes_to_load:
        if isinstance(class_full_name, (tuple, set, list)):
            load_classes(classes, class_full_name)
            continue

        try:
            klass = get_class(class_full_name)
            classes.append(klass)
        except ValueError:
            logging.warn('Invalid class name [%s]. Will be ignored.' % class_full_name)
        except AttributeError:
            logging.warn('Class [%s] not found. Will be ignored.' % class_full_name)
        except ImportError:
            logging.warn('Module [%s] not found. Will be ignored.' % class_full_name)

    return classes
