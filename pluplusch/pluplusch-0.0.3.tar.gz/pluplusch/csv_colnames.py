import csv
def colnames(fp, *args, **kwargs):
    pos = fp.tell()
    result = set(next(csv.reader(fp, *args, **kwargs)))
    fp.seek(pos)
    return result
