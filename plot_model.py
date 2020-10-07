import numpy as np
import sys
sys.path.append("../PyFancyPlots")
import plot
from contention_model import *

class comm_type_data():
    n_short = 0
    s_short = 0
    n_eager = 0
    s_eager = 0
    n_rend = 0
    s_rend = 0

    def n_msgs(self):
        return self.n_short + self.n_eager + self.n_rend

    def s_msgs(self):
        return self.s_short + self.s_eager + self.s_rend


    def model(self, arch_model, ppn):
        return (arch_model.short_model.model_func(self.n_short, self.s_short, ppn) 
                + arch_model.eager_model.model_func(self.n_eager, self.s_eager, ppn)
                + arch_model.rend_model.model_func(self.n_rend, self.s_rend, ppn))

    def print_data(self):
        print("Num: %d short, %d eager, %d rend\n" %(self.n_short, self.n_eager,
                self.n_rend))
        print("Size: %d short, %d eager, %d rend\n" %(self.s_short, self.s_eager,
                self.s_rend))

class data():
    socket_data = ""
    node_data = ""
    network_data = ""
    time = np.inf
    comm_time = np.inf
    ppn = 16
    best_byte_hops = 0
    worst_byte_hops = 0
    total_bytes = 0
    n_nodes = 512

    def __init__(self):
        self.socket_data = comm_type_data()
        self.node_data = comm_type_data()
        self.network_data = comm_type_data()

    def model_maxrate(self):
        t = self.socket_data.model(socket_model, self.ppn)
        t += self.node_data.model(node_model, self.ppn)
        t += self.network_data.model(network_model, self.ppn)
        return t
        
    def model_queue(self):
        n = (self.socket_data.n_msgs() + self.node_data.n_msgs()
                + self.network_data.n_msgs())
        return queue_model.queue_model.model_func(n)

    def print_data(self):
        print("SocketData:\n")
        self.socket_data.print_data()
        print("NodeData:\n")
        self.node_data.print_data()
        print("NetworkData:\n")
        self.network_data.print_data()

    def model_contention(self):
        model_func = contention_model.contention_model.model_func
        best_hops = self.best_byte_hops / self.total_bytes
        n_gem = self.n_nodes / 2
        avg_bytes = self.total_bytes / (n_gem) # bytes per gemini
        best_bytes = (best_hops**3) * avg_bytes
        return model_func(best_bytes)

class Level():
    AP = ""
    PTAP = ""
    Ax = ""
    Pe = ""
    PTr = ""

    def __init__(self):
        self.AP = data()
        self.PTAP = data()
        self.Ax = data()
        self.Pe = data()
        self.PTr = data()

lin_elas = list()
filename = "bw_output/model/amg_models/lin_elas_8192.out"

current_data = ""
f = open(filename, 'r')
level = -1
for line in f:
    if "Level" in line:
        level = (int)((line.rsplit('\n')[0]).rsplit(' ')[-1])
        if level == len(lin_elas):
            lin_elas.append(Level())
    elif "A*P" in line:
        current_data = lin_elas[level].AP
    elif "P.T*AP" in line:
        current_data = lin_elas[level].PTAP
    elif "A*x" in line:
        current_data = lin_elas[level].Ax
    elif "P*e" in line:
        current_data = lin_elas[level].Pe
    elif "P.T*r" in line:
        current_data = lin_elas[level].PTr

    elif "Num" in line or "Size" in line:
        n = (int)((line.rsplit('\n')[0]).rsplit(' ')[-1])
        if "Active Processes" in line:
            current_data.ppn = 16
            #current_data.ppn = n / 512
        else:
            c = ""
            if "Socket" in line:
                c = current_data.socket_data
            elif "Node" in line:
                c = current_data.node_data
            else:
                c = current_data.network_data

            if "Num" in line:
                if "Short" in line:
                    c.n_short = n
                elif "Eager" in line:
                    c.n_eager = n
                else:
                    c.n_rend = n
            else:
                if "Short" in line:
                    c.s_short = n
                elif "Eager" in line:
                    c.s_eager = n
                else:
                    c.s_rend = n
    elif "Time:" in line:
        t = (float)((line.rsplit('\n')[0]).rsplit(' ')[-1])
        if "Comm" in line:
            if t < current_data.comm_time:
                current_data.comm_time = t
        else:
            current_data.time = t
    elif "Byte" in line:
        n = (int)((line.rsplit('\n')[0]).rsplit(' ')[-1])
        if "Worst Byte Hops" in line:
            current_data.worst_byte_hops = n
        elif "Byte Hops" in line:
            current_data.best_byte_hops = n
        else:
            current_data.total_bytes = n

f.close()


if __name__ == '__main__':
    x_data = np.arange(len(lin_elas))
    
    # Plot Ax times vs max-rate model (standard)
    plot.add_luke_options()
    postal = [l.Ax.socket_data.model(postal_model, l.Ax.ppn) 
            + l.Ax.node_data.model(postal_model, l.Ax.ppn) 
            + l.Ax.network_data.model(postal_model, l.Ax.ppn) for l in lin_elas]
    max_rate = [l.Ax.socket_data.model(standard_model, l.Ax.ppn) 
            + l.Ax.node_data.model(standard_model, l.Ax.ppn) 
            + l.Ax.network_data.model(standard_model, l.Ax.ppn) for l in lin_elas]
    times = [l.Ax.comm_time for l in lin_elas]
    y_data = [times, max_rate]
    groups = ["Measured", "Max-Rate"]
    plot.barplot(x_data, y_data, groups)
    plot.add_labels("Level in AMG Hierarchy", "Time (Seconds)")
    plot.save_plot("%s/lin_elas_8192_Ax_maxrate.pdf"%fig_folder)

    # Plot AP times vs max-rate model (standard)
    plot.add_luke_options()
    postal = [l.AP.socket_data.model(postal_model, l.AP.ppn) 
            + l.AP.node_data.model(postal_model, l.AP.ppn) 
            + l.AP.network_data.model(postal_model, l.AP.ppn) for l in lin_elas]
    max_rate = [l.AP.socket_data.model(standard_model, l.AP.ppn) 
            + l.AP.node_data.model(standard_model, l.AP.ppn) 
            + l.AP.network_data.model(standard_model, l.AP.ppn) for l in lin_elas]
    times = [l.AP.comm_time for l in lin_elas]
    y_data = [times, max_rate]

    groups = ["Measured", "Max-Rate"]
    plot.barplot(x_data, y_data, groups)
    plot.add_labels("Level in AMG Hierarchy", "Time (Seconds)")
    plot.save_plot("%s/lin_elas_8192_AP_maxrate.pdf"%fig_folder)

    num_models = 3
    
    '''
    # Plot Ax times vs model
    plot.add_luke_options()
    max_rate = [l.Ax.model_maxrate() for l in lin_elas]
    queue = [l.Ax.model_queue() for l in lin_elas]
    color_palette = plot.sns.color_palette()
    times = [l.Ax.comm_time for l in lin_elas]
    contention = [l.Ax.model_contention() for l in lin_elas]
    y_data = [times, [max_rate, queue, contention]]
    labels = ["Measured", ["Max-Rate", "Queue", "Contention"]]
    plot.partially_stacked_barplot(x_data, y_data, labels)
    plot.add_labels("Level in AMG Hierarchy", "Time (Seconds)")
    plot.save_plot("%s/grad_div_8192_Ax.pdf"%fig_folder)

    # Plot AP times vs model
    plot.add_luke_options()
    max_rate = [l.AP.model_maxrate() for l in lin_elas]
    queue = [l.AP.model_queue() for l in lin_elas]
    color_palette = plot.sns.color_palette()
    times = [l.AP.comm_time for l in lin_elas]
    contention = [l.AP.model_contention() for l in lin_elas]
    y_data = [times, [max_rate, queue, contention]]
    labels = ["Measured", ["Max-Rate", "Queue", "Contention"]]
    plot.partially_stacked_barplot(x_data, y_data, labels)
    plot.add_labels("Level in AMG Hierarchy", "Time (Seconds)")
    plot.save_plot("%s/grad_div_8192_AP.pdf"%fig_folder)

    '''


