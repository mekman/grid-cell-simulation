# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.sparse import csr_matrix, lil_matrix, dok_matrix

use_sparse_matrices = True
side_length = 125 # cm


def create_grid(side_length=side_length):
    input_x = np.linspace(-side_length/2., side_length/2., num=20).reshape(20,1)
    input_x = np.tile(input_x, (20,1))
    
    input_y = np.linspace(-side_length/2., side_length/2., num=20).reshape(20,1)
    input_y = np.tile(input_y, 20)
    input_y = input_y.reshape(400,1)
    
    input_neurons = np.concatenate((input_x, input_y), axis=1)
    return input_neurons


def input_rates(time_positions):
    print 'calculating input rates...'
    input_neurons = create_grid()

    x_diff = (input_neurons[:,0].reshape(1,input_neurons.shape[0]) - time_positions[:,0].reshape(time_positions.shape[0],1))
    y_diff = (input_neurons[:,1].reshape(1,input_neurons.shape[0]) - time_positions[:,1].reshape(time_positions.shape[0],1))

    rates = np.exp(- (x_diff ** 2 + y_diff ** 2) / 50.)
    return rates

def input_rates_sparse(time_positions):
    print 'calculating input rates...'
    input_neurons = create_grid()
    # rates = lil_matrix((np.size(time_positions,0), np.size(input_neurons,0)), dtype='float32')
    # rates = np.zeros((np.size(time_positions,0), np.size(input_neurons,0)))
    rates = dok_matrix((np.size(time_positions,0), np.size(input_neurons,0)), dtype='float32')


    for i in range(np.size(time_positions,0)):
        x_diff = (input_neurons[:,0].reshape(1,input_neurons.shape[0]) - time_positions[i,0])
        y_diff = (input_neurons[:,1].reshape(1,input_neurons.shape[0]) - time_positions[i,1])

        rates_for_i = np.exp(- (x_diff ** 2 + y_diff ** 2) / 50.)
        rates_for_i[rates_for_i < 1e-2] = 0
        for j in np.nonzero(rates_for_i)[1]:
            rates[i,j] = rates_for_i[0,j]

        # if i % 100000 == 0:
        #     print 'iter no: ' + str(i / 100000)

        # rates[i,:] = rates_for_i
    return rates.tocsr()


# transforms an array of length 400 to grid of 20x20 preserving the correct positions
def reshape_vec_to_grid(vector):
    return vector.reshape((20,20))[::-1]


def test():
    #time_positions = np.random.rand(1000,3) * 125 - 62.5
    x = np.linspace(-60,60,1000).reshape(1000,1)
    #x = np.linspace(0,0,1000).reshape(1000,1)
    y = np.linspace(-60,60,1000).reshape(1000,1)
    #y = np.linspace(0,0,1000).reshape(1000,1)
    z = np.zeros((1000,1))
    time_positions = np.concatenate([x,y,z], axis=1)
    rates = input_rates(time_positions)
    sum_rates = rates.sum(axis=0)
    plt.pcolor(sum_rates.reshape(20,20))
    plt.colorbar()


def visualize_grid():
    grid = create_grid()
    plt.figure(figsize=(10, 10))
    plt.scatter(grid[:,0], grid[:,1], marker='.')

    radius = np.sqrt(50.)    
    
    for i in range(grid.shape[0]):
        circle = plt.Circle((grid[i, 0], grid[i, 1], radius), fill=False, color='b')
        plt.gcf().gca().add_artist(circle)

    limit = 70.
    axes = plt.gca()
    axes.set_xlim([-limit, limit])
    axes.set_ylim([-limit, limit])
    
    axes.add_patch(patches.Rectangle((-62.5,-62.5), 125, 125, fill=False, color='r'))


def visualize_activity(positions, rates):
    plt.figure()
    plt.plot(positions[:,0],positions[:,1])
    plt.xlim(-65,65)
    plt.ylim(-65,65)
    
    plt.figure()
    sum_rates = rates.sum(axis=0)
    sum_rates = reshape_vec_to_grid(sum_rates)
    plt.matshow(sum_rates)
    plt.colorbar()
