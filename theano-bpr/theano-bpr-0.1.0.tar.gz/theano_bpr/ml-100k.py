from bpr import *
import numpy

f = open('ml-100k/u.data')

data = numpy.zeros((943, 1682))
with open('ml-100k/u.data') as f:
    for line in f.readlines():
        user, item, rating, time = line.split('\t')
        data[int(user) - 1, int(item) - 1] = int(rating)

# leave-one-out
test = numpy.zeros((943, 1682))
for i in range(data.shape[0]):
    nonzero_indices = data[i,:].nonzero()[0]
    j = nonzero_indices[numpy.random.randint(len(nonzero_indices))]
    test[i, j] = data[i, j]
    data[i, j] = 0

for _ in range(10000):
    uu = numpy.random.randint(data.shape[0])
    nonzero = data[uu,:].nonzero()
    z = numpy.random.randint(len(nonzero[0]))
    ii = nonzero[0][z]
    zeros = numpy.where(data[uu,:] == 0)
    jj = zeros[0][numpy.random.randint(len(zeros))]
    print uu, ii, jj
    print train_model(uu, ii, jj)

auc = 0.0
for uu in range(test.shape[0]):
    auc_u = 0.0
    n = 0
    for ii in test[uu,:].nonzero()[0]:
        zeros = numpy.where((test + data)[uu,:] == 0)
        for jj in zeros[0]:
            n += 1
            if get_x_ui(uu, ii) > get_x_ui(uu, jj):
                auc_u += 1
    auc_u /= n
    print "AUC for %s: %s" % (str(uu), str(auc_u))
    auc += auc_u
auc /= data.shape[0]
print auc
