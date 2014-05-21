from ralph.discovery.models import DiskShare
import xlrd
workbook = xlrd.open_workbook('/home/kula/3par_2014_05_verified.xlsx')
with open('3par_2014_05_verified_v3.txt', 'a+') as f:
    for name in workbook.sheet_names():
        sheet = workbook.sheet_by_name(name)
        for i in xrange(sheet.nrows):
            current_row = sheet.row_values(i)
            try:
                diskshare = DiskShare.objects.get(label=current_row[0])
                f.write('{0},{1},{2},{3}\n'.format(current_row[0],1,1, diskshare.wwn))
            except DiskShare.MultipleObjectsReturned:
                diskshare = DiskShare.objects.filter(label=current_row[0])
                for i in diskshare:
                    f.write('{0},{1},{2},{3}\n'.format(current_row[0],diskshare.count(),1,i.wwn))
            except DiskShare.DoesNotExist:
                f.write('{0},{1},{2},{3}\n'.format(current_row[0],0,0,None))
