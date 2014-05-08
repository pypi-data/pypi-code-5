import theano, numpy
import theano.tensor as T
import time

theano.config.mode = 'FAST_RUN'
theano.config.floatX = 'float32'

u = T.lvector('u')
i = T.lvector('i')
j = T.lvector('j')

# Add bias regularisation

#lambda_2 = 0.1
#lambda_2 = 0.0025
lambda_u = 0.0025
lambda_i = 0.0025
lambda_j = 0.00025
learning_rate = 0.05
k = 50
#n_u = 943
#n_i = 1682
#n_u = 2195673
#n_i = 335
# tiny
#n_u = 10000
#n_i = 783
# week
n_u = 210118
n_i = 793

W = theano.shared(numpy.random.random((n_u, k)).astype('float32'), name='W')
H = theano.shared(numpy.random.random((n_i, k)).astype('float32'), name='H')

x_ui = T.dot(W[u], H[i].T).diagonal() # is that ideal? Lots of useless computations
get_x_ui = theano.function(inputs=[u, i], outputs=x_ui)
x_uj = T.dot(W[u], H[j].T).diagonal()
get_x_uj = theano.function(inputs=[u, j], outputs=x_uj)

x_uij = x_ui - x_uj
get_x_uij = theano.function(inputs=[u, i, j], outputs = x_uij)

obj = T.sum(T.log(T.nnet.sigmoid(x_uij)) - lambda_u * (W[u] ** 2).sum(axis=1) - lambda_i * (H[i] ** 2).sum(axis=1) - lambda_j * (H[j] ** 2).sum(axis=1))

cost = - obj
get_cost = theano.function(inputs=[u, i, j], outputs = cost)

g_cost_W = T.grad(cost=cost, wrt=W)
get_g_cost_W = theano.function(inputs=[u,i,j], outputs=g_cost_W)
g_cost_H = T.grad(cost=cost, wrt=H)
get_g_cost_H = theano.function(inputs=[u,i,j], outputs=g_cost_H)

updates = [ (W, W - learning_rate * g_cost_W), (H, H - learning_rate * g_cost_H) ]

train_model = theano.function(inputs=[u, i, j], outputs=cost, updates=updates)

#data = numpy.array([
#    [ 0, 0, 1, 1, 0, 0, 1, 1, 0, 1],
#    [ 0, 1, 0, 1, 0, 0, 1, 1, 0, 1],
#    [ 0, 0, 1, 0, 1, 0, 0, 0, 1, 0],
#    [ 1, 0, 0, 1, 0, 1, 0, 1, 0, 0],
#    [ 0, 1, 0, 1, 1, 0, 0, 0, 0, 1],
#    [ 0, 0, 0, 1, 0, 0, 1, 0, 0, 1],
#    [ 1, 0, 0, 0, 1, 0, 0, 1, 0, 1],
#    [ 0, 1, 1, 0, 0, 0, 0, 1, 0, 0],
#    [ 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
#    [ 1, 1, 0, 1, 0, 1, 0, 0, 0, 1],
#])
#for _ in range(1000):
#    z = numpy.random.randint(len(data.nonzero()[0]))
#    uu = data.nonzero()[0][z]
#    ii = data.nonzero()[1][z]
#    zeros = numpy.where(data[uu,:] == 0)
#    jj = zeros[0][numpy.random.randint(len(zeros))]
#    print uu, ii, jj
#    print train_model(uu, ii, jj)

