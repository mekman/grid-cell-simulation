import numpy as np
import sklearn.preprocessing as pre
import matplotlib.pyplot as plt


class FastOutputLayer:
    def __init__(self, input_layer_inputs):
        self.debug_mode = False
        self.sparse_matrix_mode = True

        # layer metaparameters
        self.output_size = 100
        self.input_size = 400
        self.network_size = (self.output_size, self.input_size)
        self.a_bounds = (0.095, 0.105)
        self.a_0 = 0.1
        self.s_bounds = (0.295, 0.315)
        self.s_0 = 0.3
        self.input_layer_inputs = input_layer_inputs  # np matrix n by 400
        self.output_layer_outputs = np.zeros((np.size(input_layer_inputs, 0), self.output_size))  # time-step x 100
        self.output_save = np.zeros(
            (int(np.size(input_layer_inputs, 0) / 100000.0 + 1), self.output_size))  # save output every 10000 timesteps
        self.weight_save = np.zeros(
            (int(np.size(input_layer_inputs, 0) / 100000.0 + 1), self.output_size * self.input_size))
        # self.g_history = np.zeros(
        #     (np.size(input_layer_inputs, 0), 1))
        # self.mu_history = np.zeros(
        #     (np.size(input_layer_inputs, 0), 1))
        # self.iter_no_history = np.zeros(
        #     (np.size(input_layer_inputs, 0), 1))
        self.max_optim_iters = 100

        # layer parameters
        self.weights = 0.9 + 0.1 * np.random.uniform(0, 1, self.network_size)  # as stated in the paper
        self.normalize_weights()
        self.avg_input_rates = np.zeros((self.input_size,))
        self.avg_firing_rate = np.zeros((self.output_size,))
        self.r_plus = 0.001 * np.ones((self.output_size,))
        self.r_minus = 0.001 * np.ones((self.output_size,))
        self.mu = 0
        self.mu_0 = 0
        self.g = 4.5
        self.g_0 = 4.5
        self.b_mu = 0.01
        self.b_g = 0.1
        self.eta = 0.05
        self.epsilon = 0.005
        self.tau_plus = .1  # seconds
        self.tau_minus = .3  # seconds
        self.delta_t = 1e-3  # seconds

    @staticmethod
    def activation_fun(g, mu, r_plus):
        val = 2.0 / np.pi * np.arctan(g * (r_plus - mu)) * 0.5 * (np.sign(r_plus - mu) + 1.0)
        return val

    # computes outputs for each time step from input layer outputs
    def process_all_inputs(self):
        for i in range(np.size(self.input_layer_inputs, 0)):  # for each time step
            # self.g = self.g_0
            # self.mu = self.mu_0
            if self.sparse_matrix_mode:
                input = np.reshape(self.input_layer_inputs[i, :].toarray(), 400)
            else:
                input = self.input_layer_inputs[i, :]
            h = np.dot(self.weights, input)  # results in size: (100,)
            self.r_plus += (1 / self.tau_plus) * (h - self.r_plus - self.r_minus) * self.delta_t
            self.r_minus += (1 / self.tau_minus) * (h - self.r_minus) * self.delta_t
            if self.debug_mode:
                all_a = []
                all_s = []
                all_g = []
                all_mu = []

            # last_iter_no = self.max_optim_iters
            for j in range(self.max_optim_iters):
                output = self.activation_fun(self.g, self.mu, self.r_plus)
                if np.any(np.isnan(output)):
                    print 'nanalert for output'
                a = np.mean(output)
                if np.sum(np.power(output, 2)) == 0:
                    s = 0
                else:
                    s = np.power(a, 2) / np.sum(np.power(output, 2)) * self.output_size  # correct formula - checked

                if self.debug_mode:
                    all_a.append(a)
                    all_s.append(s)
                    all_g.append(self.g)
                    all_mu.append(self.mu)
                if (self.a_bounds[0] < a < self.a_bounds[1]) \
                        and (self.s_bounds[0] < s < self.s_bounds[1]):
                    # last_iter_no = j
                    break

                self.mu += self.b_mu * (a - self.a_0)
                self.g += self.b_g * self.g * (s - self.s_0)

            if self.debug_mode:
                plt.plot(all_a, label='a')
                plt.plot(all_s, label='s')
                plt.legend()

                plt.title('iteration: ' + str(i))
                plt.show()
                plt.plot(all_mu, label='mu')
                plt.title('iteration: ' + str(i))
                plt.legend()
                plt.show()
                plt.plot(all_g, label='g')
                plt.title('iteration: ' + str(i))
                plt.legend()
                plt.show()

            output = self.activation_fun(self.g, self.mu, self.r_plus)
            self.output_layer_outputs[i, :] = output
            self.avg_firing_rate += self.eta * (output - self.avg_firing_rate)  # size: 100
            self.avg_input_rates += self.eta * (input - self.avg_input_rates)  # size: 400
            self.weights += self.epsilon * (
                np.outer(output, input) - np.outer(self.avg_firing_rate, self.avg_input_rates))
            self.normalize_weights()
            w = np.reshape(self.weights, np.size(self.weights), order='F')

            if i % 100000 == 0:
                index = int(i / 100000.0)
                self.output_save[index, :] = output
                self.weight_save[index, :] = w


        # np.savez("g_history", self.g_history)
        # np.savez("mu_history", self.mu_history)
        # np.savez("iter_no_history", self.iter_no_history)

    def normalize_weights(self):
        normalized_weights = pre.normalize(self.weights, norm='l2', copy='true')
        self.weights = normalized_weights


    def save_data_to_disk(self):
        np.savez("firing_rate", self.output_save)
        np.savez("weights", self.weight_save)

def main():
    layer = FastOutputLayer(np.zeros((100, 400)))
    layer.process_all_inputs()
    plt.matshow(layer.weights)
    plt.colorbar()
    plt.show()


if __name__ == '__main__':
    main()
