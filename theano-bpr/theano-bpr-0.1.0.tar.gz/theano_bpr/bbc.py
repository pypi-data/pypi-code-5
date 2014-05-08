from bpr import *
import numpy
import scipy
import time

def load_data(csv):
    data = numpy.zeros((2195673, 335))
    users = set()
    items = set()
    with open(csv) as f:
        for line in f.readlines():
            user, item = line.split(',')
            user, item = int(user), int(item)
            users.add(user)
            items.add(item)
            data[user, item] = 1.0
    return scipy.sparse.csc_matrix(data), users, items

train, train_users, train_items = load_data('data/training.csv')
test, test_users, test_items = load_data('data/testing.csv')

for z in range(10000):
    t0 = time.time()
    uu = list(train_users)[numpy.random.randint(len(train_users))]
    nonzero = train[uu,:].nonzero()
    if len(nonzero[0]) > 0:
        ii = nonzero[1][numpy.random.randint(len(nonzero[1]))]
        jj = numpy.random.randint(train.shape[1])
        while train[ii, jj] != 0:
            jj = numpy.random.randint(train.shape[1])
        #print uu, ii, jj
        t1 = time.time()
        loss = train_model(uu, ii, jj)
        print "Train model: %s in %s seconds" % (str(loss), str(time.time() - t1))
        print "Time taken: %s" % (str(time.time() - t0))
    if z % 1000 == 0:
        print "Processed %s" % str(z)

aucs = []
z = 0
total = test + train
w = W.get_value()
h = H.get_value()
for uu in train_users:
    auc_u = 0.0
    n = 0
    predictions = w[uu,:].dot(h.T)
    for ii in test[uu, :].nonzero()[1]:
        if ii in train_items:
            for jj in train_items:
                if total[uu, jj] == 0:
                    n += 1
                    if predictions[ii] > predictions[jj]:
                        auc_u += 1
    if n > 0:
        auc_u /= n
        aucs.append(auc_u)
        print "AUC for %s: %s" % (str(uu), str(auc_u))
    z += 1
    if z % 100 == 0:
        print "Current mean: %s" % (str(numpy.mean(aucs)),)

auc = numpy.mean(aucs)
print auc
