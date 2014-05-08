'''
boostrap_span.template-tag.
(C) Copyright 2014 Stuart McMillan, Useful Automation
'''
from django import template
from ..form_span import FormSpanMixin

register = template.Library()

@register.filter(name='apply_bootstrap_span')
def apply_bootstrap_span(form, args):
    """For bootstrap we need to define form fields class to have correct spanN
    (field width controlled by CSS).
    Thats what this does - deduces spanN class per field from form
    (generic form views are initialised from model)."""
    arg_list = args.split(",") if args else []
    max_span = int(arg_list[0]) if (len(arg_list)>0 and arg_list[0]) else None
    chars_per_span = int(arg_list[1]) if (len(arg_list)>1 and arg_list[1]) else None
    formSpanner = FormSpanMixin(max_span=max_span,chars_per_span=chars_per_span)
    formSpanner.alter_form_fields_class_span(target_form_instance=form)
    return form
