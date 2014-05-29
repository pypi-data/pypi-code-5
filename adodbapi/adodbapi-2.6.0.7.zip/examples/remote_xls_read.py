import sys
import adodbapi.remote

con_args = {'macro_is64bit' : ['driver', "Microsoft.ACE.OLEDB.12.0", "Microsoft.Jet.OLEDB.4.0"],
            'extended' : 'Extended Properties="Excel 8.0;HDR=Yes;IMEX=1;"'}

try:  # first command line argument will be xls file name -- default to the one written by xls_write.py
    filename = sys.argv[1]
except IndexError:
    filename = 'xx.xls'
con_args['filename'] = filename

constr = "Provider=%(driver)s;Data Source=%(filename)s;%(extended)s"

con_args['proxy_host'] = '25.79.8.220'

conn = adodbapi.remote.connect(constr, con_args)

try:  # second command line argument will be worksheet name -- default to first worksheet
    sheet = sys.argv[2]
except IndexError:
    # use ADO feature to get the name of the first worksheet
    sheet = conn.get_table_names()[0]

print('Shreadsheet=%s  Worksheet=%s' % (filename, sheet))
print('------------------------------------------------------------')
crsr = conn.cursor()
sql = "SELECT * from [%s]" % sheet
crsr.execute(sql)
for row in crsr.fetchmany(10):
    print(repr(row))
crsr.close()
conn.close()
