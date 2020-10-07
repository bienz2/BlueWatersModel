import numpy as np
from nodecomm_model import *
import sys
sys.path.append("..")
import plot

class Comm():
    node_size = 0
    ppn = ""
    ppn_times = ""
    ppn_dict = ""

    def __init__(self, node_size):
        self.node_size = node_size
        self.ppn = list()
        self.ppn_times = list()
        self.ppn_dict = dict()

    def add_ppn(self, ppn):
        if ppn not in self.ppn_dict:
            pos = len(self.ppn)
            self.ppn_dict[ppn] = pos
            self.ppn.append(ppn)
            self.ppn_times.append(np.inf)

    def add_timing(self, t, ppn):
        pos = self.ppn_dict[ppn]
        if t < self.ppn_times[pos]:
            self.ppn_times[pos] = t

def parse(filename, sizes):

    ppn = 0
    times = list()
    positions = dict()
    pos = -1
    prev_node_size = 0

    for s in sizes:
        f = open(filename%s, 'r')

        for line in f:
            if "MsgSize" in line:
                list_words = (line.rsplit('\n')[0]).rsplit(',')
                node_size = (int)(list_words[0].rsplit(' ')[-1]) * 16 * INT_SIZE
                ppn = (int)(list_words[1].rsplit(' ')[-1])
                proc_size = (int)(list_words[2].rsplit(' ')[-1]) * INT_SIZE
                if (node_size != prev_node_size):
                    if node_size in positions:
                        pos = positions[node_size]
                    else:
                        pos = len(times)
                        positions[node_size] = pos
                        times.append(Comm(node_size))
                        prev_node_size = node_size
                times[pos].add_ppn(ppn)

            elif "PPN" in line:
                list_words = (line.rsplit('\n')[0]).rsplit('\t')
                ppn = (int)(list_words[1])
                max_t = 0.0
                for i in range(2, len(list_words)):
                    if list_words[i] == "":
                        break
                    t = float(list_words[i]) / 2
                    if (t < 0):
                        break
                    if t > max_t:
                        max_t = t
                times[pos].add_timing(max_t, ppn)

    return times


def model_ab_times(times):
    data_short = list()
    rhs_short = list()
    data_eager = list()
    rhs_eager = list()
    data_rend = list()
    rhs_rend = list()
    for t in times: 
        for i in [0]: #Only looking at ppn=1
            size = t.node_size
            time = t.ppn_times[i]
            ppn = t.ppn[i]
            size /= ppn
            print(size, ppn, time)
            if size < short_cutoff:
                data_short.append([1, size])
                rhs_short.append(time)
            elif size < eager_cutoff:
                data_eager.append([1, size])
                rhs_eager.append(time)
            else:
                if ppn > 1:
                    continue
                data_rend.append([1, size])
                rhs_rend.append(time)

    params = list()
    for data,rhs in [(data_short, rhs_short), (data_eager, rhs_eager),
            (data_rend, rhs_rend)]:
        A = np.matrix(data)
        b = np.array(rhs)
        params.append(np.linalg.lstsq(A, b)[0])

    return params

def model_inj_times(times, params):
    data = list()
    rhs = list()
    for t in times: 
        size = t.node_size
        if size < eager_cutoff:
            continue
        for i in [2, 3, 4]:
            ppn = t.ppn[i]
            time = t.ppn_times[i]
            data.append([size])
            rhs.append(time - (params[2][0]))
    
    A = np.matrix(data)
    b = np.array(rhs)
    params.append(np.linalg.lstsq(A, b)[0])

    print(params)

def model_func(size, ppn, params):
    msg_size = size / ppn;
    if msg_size < short_cutoff:
        return params[0][0] + msg_size * params[0][1]
    elif msg_size < eager_cutoff:
        return params[1][0] + msg_size * params[1][1]
    else:
        t0 = params[2][0] + msg_size * params[2][1]
        t1 = params[2][0] + size * params[3]
        return max(t0, t1)


if __name__=='__main__':
    model = False 
    plot_points = True

    plot.add_luke_options()
    ax = plot.get_ax()

    fn = "bw_output/model/imbalance/node_imbalanced_nr_%d.out"
    times = parse(fn, [1,2,3])

    params = model_ab_times(times)
    model_inj_times(times, params)

    if plot_points:
        min_y = np.inf
        max_y = 0
        min_x = np.inf
        max_x = 0

        ppn_list = times[0].ppn
        sizes = [t.node_size for t in times]
        colors = plot.sns.color_palette(n_colors = len(ppn_list))

        for i in range(len(ppn_list)):
            x_data = list()
            y_data = list()
            model = list()

            ppn = ppn_list[i]
            if ppn == 2: 
                continue
            for t in times:
                size = t.node_size
                model.append(model_func(size, ppn, params))
                time = t.ppn_times[i]
                y_data.append(time)
                x_data.append(size)
                if time < min_y:
                    min_y = time
                if time > max_y:
                    max_y = time

            plot.scatter_plot(x_data, y_data, color = colors[i], 
                    label = "PPN %d"%(ppn))
            plot.line_plot(model, x_data, color = colors[i]);


        ax.set_ylim(0.9*min_y, 1.1*max_y)
        plot.set_scale('log', 'log')
        plot.add_anchored_legend(ncol=4)
        plot.add_labels("Number of Bytes Sent by Node", "Time to Send Message")
        plot.save_plot("node_model_nr.pdf")
        
