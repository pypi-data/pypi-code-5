# -*- coding: utf-8 -*-

import itertools
import os.path as osp
from logilab.common.shellutils import ProgressBar

from cubes.codenaf import dbf

DATADIR= osp.join(osp.dirname(dbf.__file__), 'data')

INTSET = frozenset('1 2 3 4 5 6 7 8 9'.split())

NAF_N1 = osp.join(DATADIR, 'naf2008_liste_n1.dbf')
NAF_N2 = osp.join(DATADIR, 'naf2008_liste_n2.dbf')
NAF_N3 = osp.join(DATADIR, 'naf2008_liste_n3.dbf')
NAF_N4 = osp.join(DATADIR, 'naf2008_liste_n4.dbf')
NAF_N5 = osp.join(DATADIR, 'naf2008_liste_n5.dbf')
NAF_NIV = osp.join(DATADIR, 'naf2008_5_niveaux.dbf')

n1 = dbf.readDbf(NAF_N1)
n2 = dbf.readDbf(NAF_N2)
n3 = dbf.readDbf(NAF_N3)
n4 = dbf.readDbf(NAF_N4)
n5 = dbf.readDbf(NAF_N5)
niveaux = dbf.readDbf(NAF_NIV)

classif = rql('Any C WHERE C is Classification, C name "CodeNAF"')[0][0]

# FIXME #531967: migration script can't deactivate hooks
#repo.hm.deactivate_verification_hooks()
#from cubes.keyword import hooks
#repo.hm.unregister_hook(hooks.SetIncludedInRelationHook)

rows = list(itertools.chain(n1,n2,n3,n4,n5))
bar = ProgressBar(len(rows), title='-> inserting %s NAF codes ' % len(rows))
for row in rows:
    rql('INSERT CodeKeyword K: K code %(c)s, K name %(n)s, K included_in C '
        'WHERE C eid %(cl)s',
        {'c': row['CODE'].strip().decode('cp850'),
         'n': row['LIBELL\x90'].decode('cp850'),
         'cl': classif})
    bar.update()
    bar.refresh()
commit()
print

bar = ProgressBar(len(niveaux), title='-> linking NAF codes ')
done = set()
for row in niveaux:
    for i in range(1, 5):
        child = row['NIV%i'%(i+1)].strip().decode('cp850')
        parent = row['NIV%i'%i].strip().decode('cp850')
        if i == 2 and parent in INTSET:
            parent = u'0%s' % parent
        elif i == 1 and child in INTSET:
            child = u'0%s' % child
        if (child, parent) not in done:
            rql('SET C subkeyword_of K WHERE C code %(c)s, K code %(k)s',
                {'c': child, 'k': parent})
            done.add( (child, parent) )
    bar.update()
    bar.refresh()
commit()
print
