from sphinx.domains.python import PyXRefRole


def setup(app):
    """Install the plugin.

    :param app: Sphinx application context.
    """
    app.add_role('map', mapping_role)
    app.add_config_value('xref_mapping_dict', None, 'env')


def mapping_role(name, rawtext, text, lineno, inliner,
                 options={}, content=[]):
    # Get the dictionary set in the conf.py
    # eg.
    #     xref_mapping_dict = { 'key': ('class', 'full.package.key')}
    map = inliner.document.settings.env.app.config.xref_mapping_dict

    # If the 'key' exists in our mapping, that map it
    if text in map:
        role_type, full_package = map[text]
        # Replace the text with the correct 'pretty' syntax
        new_text = '{} <{}>'.format(text, full_package)
        # Turn this in to a proper sphinx declaration
        new_rawtext = ':{}:`{}`'.format(role_type, new_text)

        # Return a python x-reference
        py_xref = PyXRefRole()
        return py_xref('py:' + role_type, new_rawtext, new_text, lineno,
                       inliner, options=options, content=content)
    else:
        msg = inliner.reporter.error(
            'Failed to find mapping for {}'.format(text), line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]