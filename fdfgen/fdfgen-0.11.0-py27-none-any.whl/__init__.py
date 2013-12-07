# -*- coding: utf-8 -*-
"""
Port of the PHP forge_fdf library by Sid Steward
(http://www.pdfhacks.com/forge_fdf/)

Anders Pearson <anders@columbia.edu> at Columbia Center For New Media Teaching
and Learning <http://ccnmtl.columbia.edu/>
"""

__author__ = "Anders Pearson <anders@columbia.edu>"
__credits__ = ("Sébastien Fievet <zyegfryed@gmail.com>",
               "Brandon Rhodes <brandon@rhodesmill.org>",
               "Robert Stewart <https://github.com/rwjs>",
               "Evan Fredericksen <https://github.com/evfredericksen>")

import codecs


def smart_encode_str(s):
    """Create a UTF-16 encoded PDF string literal for `s`."""
    try:
        utf16 = s.encode('utf_16_be')
    except AttributeError:  # ints and floats
        utf16 = str(s).encode('utf_16_be')
    safe = utf16.replace(b'\x00)', b'\x00\\)').replace(b'\x00(', b'\x00\\(')
    return b''.join((codecs.BOM_UTF16_BE, safe))


def handle_hidden(key, fields_hidden):
    if key in fields_hidden:
        return b"/SetF 2"
    else:
        return b"/ClrF 2"


def handle_readonly(key, fields_readonly):
    if key in fields_readonly:
        return b"/SetFf 1"
    else:
        return b"/ClrFf 1"


def handle_data_strings(fdf_data_strings, fields_hidden, fields_readonly):
    for (key, value) in fdf_data_strings:
        if isinstance(value, bool) and value:
            value = b'/Yes'
        elif isinstance(value, bool) and not value:
            value = b'/Off'
        else:
            value = b''.join([b' (', smart_encode_str(value), b')'])
        yield b''.join([b'<<\n/V', value, b'\n/T (',
                        smart_encode_str(key), b')\n',
                        handle_hidden(key, fields_hidden), b'\n',
                        handle_readonly(key, fields_readonly), b'\n>>\n'])


def handle_data_names(fdf_data_names, fields_hidden, fields_readonly):
    for (key, value) in fdf_data_names:
        yield b''.join([b'<<\n/V /', smart_encode_str(value), b'\n/T (',
                        smart_encode_str(key), b')\n',
                        handle_hidden(key, fields_hidden), b'\n',
                        handle_readonly(key, fields_readonly), b'\n>>\n'])


def forge_fdf(pdf_form_url="", fdf_data_strings=[], fdf_data_names=[],
              fields_hidden=[], fields_readonly=[]):
    """Generates fdf string from fields specified

    pdf_form_url is just the url for the form. fdf_data_strings and
    fdf_data_names are arrays of (key,value) tuples for the form fields.
    fields_hidden is a list of field names that should be hidden.
    fields_readonly is a list of field names that should be readonly.

    The result is a string suitable for writing to a .fdf file.

    """
    fdf = [b'%FDF-1.2\n%\xe2\xe3\xcf\xd3\r\n']
    fdf.append(b'1 0 obj\n<<\n/FDF\n')
    fdf.append(b'<<\n/Fields [\n')
    fdf.append(b''.join(handle_data_strings(fdf_data_strings,
                                            fields_hidden, fields_readonly)))
    fdf.append(b''.join(handle_data_names(fdf_data_names,
                                          fields_hidden, fields_readonly)))
    if pdf_form_url:
        fdf.append(b''.join(b'/F (', smart_encode_str(pdf_form_url), b')\n'))
    fdf.append(b']\n')
    fdf.append(b'>>\n')
    fdf.append(b'>>\nendobj\n')
    fdf.append(b'trailer\n\n<<\n/Root 1 0 R\n>>\n')
    fdf.append(b'%%EOF\n\x0a')
    return b''.join(fdf)


if __name__ == "__main__":
    # a simple example of using fdfgen
    # this will create an FDF file suitable to fill in
    # the vacation request forms we use at work.

    from datetime import datetime
    fields = [('Name', 'Anders Pearson'),
              ('Date', datetime.now().strftime("%x")),
              ('Request_1', 'Next Monday through Friday'),
              ('Request_2', ''),
              ('Request_3', ''),
              ('Total_days', 5),
              ('emergency_phone', '857-6309')]
    fdf = forge_fdf(fdf_data_strings=fields)
    fdf_file = open("vacation.fdf", "wb")
    fdf_file.write(fdf)
    fdf_file.close()

    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", "-o",
        help="FDF File to output to",
        default='vacation.fdf',
        type=argparse.FileType('wb'))
    parser.add_argument(
        "--fields", "-f",
        help="Fields used in form; syntax is fieldname=fieldvalue",
        default=fields,
        nargs='*')
    args = parser.parse_args()
    if args.fields is not fields:
        for e, x in enumerate(args. fields):
            args.fields[e] = x.split('=')
    fdf = forge_fdf(fdf_data_strings=args.fields)
    args.output.write(fdf)
    args.output.close()
