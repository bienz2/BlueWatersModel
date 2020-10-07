import numpy as np
import sys
sys.path.append("..")
import plot
from contention_model import *

class ArchData():
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



class Data(object):
    socket_data = ""
    node_data = ""
    network_data = ""
    time = np.inf
    comm_time = np.inf
    ppn = 16
    best_byte_hops = 0
    total_bytes = 0
    n_nodes = 512

    def __init__(self):
        self.socket_data = ArchData()
        self.node_data = ArchData()
        self.network_data = ArchData()

    def model_maxrate(self):
        t = self.socket_data.model(socket_model, self.ppn)
        t += self.node_data.model(node_model, self.ppn)
        t += self.network_data.model(network_model, self.ppn)
        return t
        
    def model_queue(self):
        n = (self.socket_data.n_msgs() + self.node_data.n_msgs()
                + self.network_data.n_msgs())
        return queue_model.queue_model.model_func(n)

    def model_contention(self):
        if self.total_bytes == 0:
            return 0

        model_func = contention_model.contention_model.model_func
        best_hops = self.best_byte_hops / self.total_bytes
        n_gem = self.n_nodes / 2
        avg_bytes = self.total_bytes / (n_gem) # bytes per gemini
        best_bytes = (best_hops**3) * avg_bytes
        return model_func(best_bytes)

    def num_msgs(self):
        return (self.socket_data.n_msgs() + self.node_data.n_msgs() +
            self.network_data.n_msgs())

    def print_data(self):
        print("SocketData:\n")
        self.socket_data.print_data()
        print("NodeData:\n")
        self.node_data.print_data()
        print("NetworkData:\n")
        self.network_data.print_data()

class NAPData(Data, object):
    num_L = 0
    num_S = 0
    num_R = 0
    num_G = 0

    def model_queue(self):
        return (queue_model.queue_model.model_func(self.num_L)
            + queue_model.queue_model.model_func(self.num_S)
            + queue_model.queue_model.model_func(self.num_R)
            + queue_model.queue_model.model_func(self.num_G))

class System():
    mat = ""
    tap_mat = ""
    vec = ""
    tap_vec = ""

    def __init__(self):
        self.mat = Data()
        self.tap_mat = NAPData()
        self.vec = Data()
        self.tap_vec = NAPData()

class Level():
    A = ""
    S = ""
    P = ""

    def __init__(self):
        self.A = System()
        self.S = System()
        self.P = System()

aniso = list()
filename = "bw_output/model/amg_models/aniso_8192.out"

current_data = ""
f = open(filename, 'r')
level = -1
for line in f:
    if "Level" in line:
        level = (int)((line.rsplit('\n')[0]).rsplit(' ')[-1])
        if level == len(aniso):
            aniso.append(Level())
    elif "Communication" in line:
        if "A " in line:
            current_data = aniso[level].A
        elif "S " in line:
            current_data = aniso[level].S
        elif "P " in line:
            current_data = aniso[level].P
        
        if "Vector" in line:
            if "TAP" in line:
                current_data = current_data.tap_vec
            else:
                current_data = current_data.vec
        else:
            if "TAP" in line:
                current_data = current_data.tap_mat
            else:
                current_data = current_data.mat

    elif "Num" in line or "Size" in line:
        n = (int)((line.rsplit('\n')[0]).rsplit(' ')[-1])
        if "Active Processes" in line:
            current_data.ppn = 16
        elif "Max" in line:
            if "Max Num L" in line:
                current_data.num_L = n
            elif "Max Num S" in line:
                current_data.num_S = n
            elif "Max Num R" in line:
                current_data.num_R = n
            elif "Max Num G" in line:
                current_data.num_G = n
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
    x_data = np.arange(len(aniso))
    
    times = [l.A.vec.comm_time for l in aniso]
    rel_times = [t / times[0] for t in times]
    n_msgs = [l.A.vec.num_msgs() for l in aniso]
    rel_n_msgs = [m / n_msgs[0] for m in n_msgs]
    plot.add_luke_options()
    color_palette = plot.sns.color_palette()
    y_data = [rel_times, rel_n_msgs]
    labels = ["Time", "Num Msgs"]
    plot.barplot(x_data, y_data, labels)
    plot.add_labels("Level in AMG Hierarchy", "Relative Count")
    plot.save_plot("%s/aniso_8192_A_vec_compare.pdf"%fig_folder)

    times = [l.P.vec.comm_time for l in aniso]
    print times
    rel_times = [t / times[0] for t in times]
    n_msgs = [l.P.vec.num_msgs() for l in aniso]
    rel_n_msgs = [m / n_msgs[0] for m in n_msgs]
    plot.add_luke_options()
    color_palette = plot.sns.color_palette()
    y_data = [rel_times, rel_n_msgs]
    labels = ["Time", "Num Msgs"]
    plot.barplot(x_data, y_data, labels)
    plot.add_labels("Level in AMG Hierarchy", "Relative Count")
    plot.save_plot("%s/aniso_8192_P_vec_compare.pdf"%fig_folder)

    times = [l.S.vec.comm_time for l in aniso]
    rel_times = [t / times[0] for t in times]
    n_msgs = [l.S.vec.num_msgs() for l in aniso]
    rel_n_msgs = [m / n_msgs[0] for m in n_msgs]
    plot.add_luke_options()
    color_palette = plot.sns.color_palette()
    y_data = [rel_times, rel_n_msgs]
    labels = ["Time", "Num Msgs"]
    plot.barplot(x_data, y_data, labels)
    plot.add_labels("Level in AMG Hierarchy", "Relative Count")
    plot.save_plot("%s/aniso_8192_S_vec_compare.pdf"%fig_folder)

    
    times = [l.A.mat.comm_time for l in aniso]
    rel_times = [t / times[0] for t in times]
    n_msgs = [l.A.vec.num_msgs() for l in aniso]
    rel_n_msgs = [m / n_msgs[0] for m in n_msgs]
    plot.add_luke_options()
    color_palette = plot.sns.color_palette()
    y_data = [rel_times, rel_n_msgs]
    labels = ["Time", "Num Msgs"]
    plot.barplot(x_data, y_data, labels)
    plot.add_labels("Level in AMG Hierarchy", "Relative Count")
    plot.save_plot("%s/aniso_8192_A_mat_compare.pdf"%fig_folder)

    times = [l.P.mat.comm_time for l in aniso]
    rel_times = [t / times[0] for t in times]
    n_msgs = [l.P.vec.num_msgs() for l in aniso]
    rel_n_msgs = [m / n_msgs[0] for m in n_msgs]
    plot.add_luke_options()
    color_palette = plot.sns.color_palette()
    y_data = [rel_times, rel_n_msgs]
    labels = ["Time", "Num Msgs"]
    plot.barplot(x_data, y_data, labels)
    plot.add_labels("Level in AMG Hierarchy", "Relative Count")
    plot.save_plot("%s/aniso_8192_P_mat_compare.pdf"%fig_folder)

    times = [l.S.mat.comm_time for l in aniso]
    rel_times = [t / times[0] for t in times]
    n_msgs = [l.S.vec.num_msgs() for l in aniso]
    rel_n_msgs = [m / n_msgs[0] for m in n_msgs]
    plot.add_luke_options()
    color_palette = plot.sns.color_palette()
    y_data = [rel_times, rel_n_msgs]
    labels = ["Time", "Num Msgs"]
    plot.barplot(x_data, y_data, labels)
    plot.add_labels("Level in AMG Hierarchy", "Relative Count")
    plot.save_plot("%s/aniso_8192_S_mat_compare.pdf"%fig_folder)


