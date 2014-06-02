# encoding=utf-8
import logging
import shutil
from subprocess import call
from tempfile import NamedTemporaryFile

from .settings import WKHTMLTOPDF_CMD


binary_options = {
    'low_quality': '-l',
    'quiet': '-q',
    'grayscale': '-g',
    'disable_javascript': '--disable-javascript',
}

argument_options = {
    'margin_bottom': '--margin-bottom',
    'margin_left': '--margin-left',
    'margin_top': '--margin-top',
    'orientation': '-O',
    'page_size': '-s',
    'encoding': '--encoding',
    'javascript_wait': '--javascript-delay',
    'stylesheet': '--user-style-sheet',
    'jpeg_image_quality': '--image-quality'
}

default_options = dict(
    low_quality=True, quiet=True, jpeg_image_quality=70
)


def get_options(in_file, out_file, **kwargs):
    new_kwargs = {}
    new_kwargs.update(default_options)
    new_kwargs.update(kwargs)
    options = [WKHTMLTOPDF_CMD]

    for k, v in new_kwargs.items():
        if isinstance(v, bool) and k in binary_options and v:
            if v:
                options.append(binary_options[k])
        elif k in argument_options:
            options.extend([argument_options[k], str(v)])
        else:
            raise ValueError('Invalid argument: {}={}'.format(k, v))
    options.extend([in_file, out_file])

    return options


def html_to_pdf(html, delete_html=True, delete_pdf=True, **kwargs):
    html_file = NamedTemporaryFile(delete=delete_html, suffix='.html')
    html_file.write(html.encode('utf-8'))
    html_file.flush()

    source = html_file.name

    pdf_file = NamedTemporaryFile(delete=delete_pdf, suffix='.pdf')

    options = get_options(source, pdf_file.name, **kwargs)
    logging.info("Call: %s", " ".join(options))
    call(options)

    html_file.close()

    return pdf_file


def html_to_pdf_file(html, to_file, **kwargs):
    pdf = html_to_pdf(html, **kwargs)
    shutil.copy(pdf.name, to_file)
    pdf.close()

    return open(to_file, 'rb')
