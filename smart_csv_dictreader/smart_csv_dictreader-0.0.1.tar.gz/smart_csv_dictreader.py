__version__ = '0.0.1'

def DictReader(fp, *args, **kwargs):
    '''
    Produce a csv.DictReader without specifying the fieldnames.
    Arguments get passed to csv.DictReader.
    '''
    import csv

    position = fp.tell()
    header = next(csv.reader(fp, *args, **kwargs))
    fp.seek(position)

    _kwargs = dict(kwargs)
    _kwargs['fieldnames'] = _kwargs.get('fieldnames', header)
    _kwargs['restval'] = _kwargs.get('restval', '')
    data = csv.DictReader(fp, *args, **_kwargs)
    next(data) # skip the header
    return data
