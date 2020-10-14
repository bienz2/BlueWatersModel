import numpy as np
from arch_model import *

class MaxRateModel(Model, object):
    def add_timing(self, n_msgs, s_msgs, ppn, time):
        self.times.append(time)
        if ppn < 4:
            self.data.append([n_msgs, s_msgs, 0])
        else:
            self.data.append([n_msgs, 0, ppn*s_msgs])

    def calc_model(self):
        t = list()
        d = list()
        for i in range(len(self.data)):
            if self.data[i][2] == 0:
                t.append(self.times[i])
                d.append([self.data[i][0], self.data[i][1]])
        A = np.matrix(d)
        b = np.array(t)
        alpha, beta = np.linalg.lstsq(A, b)[0]
        t = list()
        d = list()
        for i in range(len(self.data)):
            if self.data[i][1] == 0:
                t.append(self.times[i] - self.data[i][0]*alpha)
                d.append([self.data[i][2]])
        A = np.matrix(d)
        b = np.array(t)
        n = np.linalg.lstsq(A, b)[0]
        self.variables = [alpha, beta, n]

    def model_func(self, n_msgs, s_msgs, ppn):
        if len(self.variables) == 0:
            return 0
        if ppn >= 4:
            return (self.variables[0] * n_msgs) + ((ppn*s_msgs) * self.variables[2])
        else:
            return self.variables[0] * n_msgs + self.variables[1] * s_msgs            

class LocalModel(Model):
    def add_timing(self, n_msgs, s_msgs, ppn, time):
        self.times.append(time)
        self.data.append([n_msgs, s_msgs])

    def model_func(self, n_msgs, s_msgs, ppn):
        if len(self.variables) < 2:
            return 0
        return self.variables[0] * n_msgs + self.variables[1] * s_msgs

class StandardArch(Arch):
    def __init__(self, ModelClass):
        self.short_model = LocalModel()
        self.eager_model = LocalModel()
        self.rend_model = ModelClass()
        self.model_calculated = False

    def add_timing(self, n_msgs, s_msgs, ppn, time):
        msg_size = s_msgs / n_msgs
        if msg_size < short_cutoff:
            self.short_model.add_timing(n_msgs, s_msgs, ppn, time)
        elif msg_size < eager_cutoff:
            self.eager_model.add_timing(n_msgs, s_msgs, ppn, time)
        else:
            self.rend_model.add_timing(n_msgs, s_msgs, ppn, time)




filenames = ["bw_output/orig/max_rate", 
        "bw_output/on_node/on_node.out",
        "bw_output/on_node/on_socket.out"]

# Models on CRAY only 
postal_model = StandardArch(LocalModel)
standard_model = StandardArch(MaxRateModel)
socket_model = StandardArch(LocalModel)
#network_model = StandardArch(MaxRateModel)
network_model = StandardArch(LocalModel)
node_model = StandardArch(LocalModel)

# Standard Max-Rate
times = list()
data = list()
for fn in filenames:
    time_list, data_list = parse(fn, standard_model)
    for t in time_list:
        times.append(t)
    for d in data_list:
        data.append(d)
standard_model.short_model.variables = [4.0e-06, 1.6e-09]
standard_model.eager_model.variables = [1.1e-05, 5.9e-10]
standard_model.rend_model.variables = [2.0e-05, 2.8e-10, 1.8e-10]
standard_model.model_calculated = True
print ("Standard Model:\n")
standard_model.print_model()

postal_model.short_model.variables = [4.0e-06, 1.6e-09]
postal_model.eager_model.variables = [1.1e-05, 5.9e-10]
postal_model.rend_model.variables = [2.0e-05, 2.8e-10]
postal_model.model_calculated = True


# Off-Node
network_times, network_data = parse(filenames[0], network_model)
network_model.calc_model()
print ("Off-Node Model:\n")
network_model.print_model()

# On-Node
node_times, node_data = parse(filenames[1], node_model)
node_model.calc_model()
print ("On-Node Model:\n")
node_model.print_model()

# On-Socket
socket_times, socket_data = parse(filenames[2], socket_model)
socket_model.calc_model()
print ("On-Socket Model:\n")
socket_model.print_model()


if __name__ == '__main__':

    plot.color_ctr = 0

    #network_model.plot_model(network_times, network_data, "%s/alpha_beta_network.pdf"%fig_folder,
    #        label = "Network")
    #network_model.plot_model(network_times, network_data, "%s/max_rate_network.pdf"%fig_folder,
    #        label = "Network")
    
    #node_model.plot_model(node_times, node_data, "%s/max_rate_node.pdf"%fig_folder, label =
    #        "On-Node")
    #socket_model.plot_model(socket_times, socket_data, "%s/max_rate_socket.pdf"%fig_folder, label
    #        = "On-Socket")

    #plot.color_ctr = 0
    #network_model.plot_model(network_times, network_data, label = "Network", finished = False)
    plot.set_palette(palette='deep')
    plot.add_luke_options()
    node_model.plot_model(node_times, node_data, label = "On-Node", finished = False)
    socket_model.plot_model(socket_times, socket_data, 
            fn = "%s/max_rate_compare_node.pdf"%fig_folder, label = "On-Socket")

    #plot.color_ctr = 0
    #standard_model.plot_model(times, data,
    #    "%s/max_rate_standard.pdf"%fig_folder, label = "MaxRate")
    
