from bpr_minibatch import *
import numpy
import scipy
import time
import sys
from collections import defaultdict

users_to_index = {}
items_to_index = {}

def load_data(csv):
    users = set()
    items = set()
    data = defaultdict(list)
    u, i, n = 0, 0, 0
    with open(csv) as f:
        for line in f.readlines():
            user, item = line.split(',')
            user, item = int(user), item
            if not users_to_index.has_key(user):
                users_to_index[user] = u
                u += 1
            if not items_to_index.has_key(item):
                items_to_index[item] = i
                i += 1
            data[users_to_index[user]].append(items_to_index[item])
            n += 1
            items.add(items_to_index[item])
    return data, n, items

def to_sparse(data):
    ij = numpy.array(data).T
    data = numpy.ones(len(data), dtype='int32')
    return scipy.sparse.csc_matrix((data, ij), shape=(len(users_to_index.keys()), len(items_to_index.keys())), dtype='int32')

train_data, train_n, train_items = load_data('week/training.csv')
test_data, test_n, test_items = load_data('week/testing.csv')
print len(users_to_index.keys())
print len(items_to_index.keys())

print "Generating training set"
sgd_users = numpy.array(train_data.keys())[numpy.random.randint(len(train_data.keys()), size=1*train_n)]
sgd_pos_items = []
sgd_neg_items = []
for sgd_user in sgd_users:
    pos_item = train_data[sgd_user][numpy.random.randint(len(train_data[sgd_user]))]
    sgd_pos_items.append(pos_item)
    neg_item = numpy.random.randint(len(train_items))
    while neg_item in train_data[sgd_user]:
        neg_item = numpy.random.randint(len(train_items))
    sgd_neg_items.append(neg_item)

batch_size = 1000
z = 0
t0 = time.time()
while (z+1)*batch_size < len(sgd_users):
    loss = train_model(
        sgd_users[z * batch_size: (z+1) * batch_size], 
        sgd_pos_items[z * batch_size: (z+1) * batch_size], 
        sgd_neg_items[z * batch_size: (z+1) * batch_size]
    )
    #print "Train model: %s in %s seconds" % (str(loss), str(time.time() - t1))
    z += 1
    t1 = time.time()
    print "Processed %s ( %.0f%% ) in %s" % (str(z*batch_size), 100.0 * float(z*batch_size)/len(sgd_users), str(t1 - t0))
    t0 = t1

aucs = []
z = 0
w = W.get_value()
h = H.get_value()
for uu in train_data.keys():
    auc_u = 0.0
    n = 0
    predictions = w[uu,:].dot(h.T)
    for ii in test_data[uu]:
        if ii in train_items:
            for jj in train_items:
                if jj not in test_data[uu] and jj not in train_data[uu]:
                    n += 1
                    if predictions[ii] > predictions[jj]:
                        auc_u += 1
    if n > 0:
        auc_u /= n
        aucs.append(auc_u)
        # print "AUC for %s: %s" % (str(uu), str(auc_u))
    z += 1
    if z % 100 == 0:
        print "Current AUC mean (%s samples): %s" % (str(z), str(numpy.mean(aucs)))

auc = numpy.mean(aucs)
print auc
