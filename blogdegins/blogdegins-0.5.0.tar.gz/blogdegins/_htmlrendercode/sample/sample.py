# -*- encoding: utf-8 -*-
from ghtml.c_ghtml import GHtml
from ginsfsm.gconfig import add_gconfig

sample_data = {
    'myname': 'Blogdegins.',
}

Sample_CONFIG = {
    'gaplic_namespace': [
        str, '', 0, None,
        'namespace of gaplic, to store callbacks.',
    ],
    'sample_options': [
        dict,
        {
            # See default values in the partner javascript file.
        },
        0,
        None,
        'A dictionary containing the javascript options.'
    ],
}


class Sample(GHtml):
    def __init__(self, fsm=None, gconfig=None):
        gconfig = add_gconfig(gconfig, Sample_CONFIG)
        super(Sample, self).__init__(fsm=fsm, gconfig=gconfig)

    def start_up(self):
        pass

    def render(self, **kw):
        kw.update(**sample_data)
        return super(Sample, self).render(**kw)


def create_sample(name, parent, **kw):
    """ Remember put in parent python code:

        from sample import create_sample
        create_sample(
            'sample',  # the name you have to put in parent mako: ${sample}
            self,
        )
    """
    sample = parent.create_gobj(
        name,
        Sample,
        parent,
        template='/%s/htmlrendercode/ibterm/sample/sample.mako' % (
            __package__.split('.')[0]),
        **kw
    )
    return sample

