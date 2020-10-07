DOUBLE_SIZE = 8
INT_SIZE = 4


short_cutoff = 500
eager_cutoff = 8000

fig_folder = "."

import numpy as np
import pyfancyplot.plot as plot

class Model(object):
    times = ""
    data = ""
    variables = ""

    def __init__(self):
        self.times = list()
        self.data = list()

    def calc_model(self):
        if len(self.times):
            A = np.matrix(self.data)
            b = np.array(self.times)
            self.variables = np.linalg.lstsq(A, b)[0]

    def print_model(self):
        for v in self.variables:
            print("%e\t"%v)
        print("\n")


class Arch(object):
    short_model = ""
    eager_model = ""
    rend_model = ""
    model_calculated = ""

    def __init__(self, ModelClass):
        self.short_model = ModelClass()
        self.eager_model = ModelClass()
        self.rend_model = ModelClass()
        self.model_calculated = False

    def calc_model(self):
        self.short_model.calc_model()
        self.eager_model.calc_model()
        self.rend_model.calc_model()
        self.model_calculated = True

    def print_model(self):
        if not self.model_calculated:
            self.calc_model()
        print("Short: ")
        self.short_model.print_model()
        print("Eager: ")
        self.eager_model.print_model()
        print("Rend: ")
        self.rend_model.print_model()

    def model_func(self, n_msgs, s_msgs, ppn):
        msg_size = s_msgs / n_msgs
        t = 0
        if msg_size < short_cutoff:
            t += self.short_model.model_func(n_msgs, s_msgs, ppn)
        elif msg_size < eager_cutoff:
            t += self.eager_model.model_func(n_msgs, s_msgs, ppn)
        else:
            t += self.rend_model.model_func(n_msgs, s_msgs, ppn)
        return t

    def plot_model(self, times, data, fn = None, label = None, finished = True):
        plot.add_luke_options()
        plot.set_scale('log', 'log')
        plot.set_ylim(1e-7, 1e-3)
        plot.set_xlim(1e0, 1e6)

        model_sizes = sorted(list(set([d[1] for d in data])))
        model_16 = [self.model_func(1, s, 16) for s in model_sizes]
        model_1 = [self.model_func(1, s, 1) for s in model_sizes]

        if 0:
            max_size = max([d[1] for d in data])
            model_sizes = sorted(list(set([d[1] for d in data if (d[1] % 16 == 0)])))
            model_16 = [self.model_func(1, s/16, 16) for s in model_sizes]
            model_4 = [self.model_func(1, s/4, 4) for s in model_sizes]
            model_1 = [self.model_func(1, s, 1) for s in model_sizes]

            color_16 = plot.next_color()
            color_4 = plot.next_color()
            color_1 = plot.next_color()
            idx_16 = [i for i in range(len(data)) if data[i][2] == 16 and
                data[i][1]*16 in model_sizes]
            idx_4 = [i for i in range(len(data)) if data[i][2] == 4 and 
                data[i][1]*4 in model_sizes]
            idx_1 = [i for i in range(len(data)) if data[i][2] == 1 and 
                data[i][1] in model_sizes]
            plot.scatter_plot([data[i][1]*16 for i in idx_16], 
                    [times[i] for i in idx_16], color = color_16)
            plot.scatter_plot([data[i][1]*4 for i in idx_4], 
                    [times[i] for i in idx_4], color = color_4)
            plot.scatter_plot([data[i][1] for i in idx_1], 
                    [times[i] for i in idx_1], color = color_1)

            #plot.line_plot(model_16, model_sizes, color=color_16, label="PPN 16")
            #plot.line_plot(model_4, model_sizes, color=color_4, label="PPN 4")
            #plot.line_plot(model_1, model_sizes, color=color_1, label="PPN 1")
        
        equal = True
        for i in range(len(model_sizes)):
            if model_16[i] != model_1[i]:
                equal = False
                break

        if not equal:
            color_16 = plot.next_color()
            color_1 = plot.next_color()
            plot.line_plot(model_16, model_sizes,
                    color = color_16, label = "%s (PPN $\geq$ 4)"%label)
            plot.line_plot(model_1, model_sizes,
                    color = color_1, label = "%s (PPN $<$ 4)"%label)
            idx_n = [i for i in range(len(data)) if data[i][2] >= 4]
            idx_1 = [i for i in range(len(data)) if data[i][2] < 4]
            plot.scatter_plot([data[i][1] for i in idx_n], [times[i] for i in idx_n], color = color_16)
            plot.scatter_plot([data[i][1] for i in idx_1], [times[i] for i in idx_1], color = color_1)
        else:
            color = plot.next_color()
            plot.line_plot(model_1, model_sizes, color = color, label = label)
            x_data = [data[i][1] for i in range(len(data))]
            y_data = [times[i] for i in range(len(data))]            
            plot.scatter_plot(x_data, y_data, color = color)
        

        plot.add_labels("Number of Bytes Communicated", "Time (seconds)")
        plot.set_scale('log', 'log')
        plot.set_ylim(1e-7, 1e-3)
        plot.set_xlim(0.9*min(model_sizes), 1.1*max(model_sizes))

        
        if finished:
            if len(plot.plt.gca().lines) > 1:
                plot.add_anchored_legend()
            if fn:
                plot.save_plot("%s"%fn)
            else:
                plot.display_plot()
        
        #plot.add_anchored_legend(ncol=3)
        #plot.save_plot("../../Figures/models/node_bytes_ppn.pdf")

def parse(filename, model, arch_model = None, n_procs = 16):
    times = list()
    data = list()

    n_msgs = -1
    s_msgs = -1
    
    f = open(filename, 'r')
    for line in f:
        if "Pingpong" in line or "master" in line or "partner" in line:
            continue
        if "Nodecomm" in line or "srun" in line:
            continue
        elif "Num Msgs" in line:
            n_msgs = (int)((line.rsplit('\n')[0]).rsplit(' ')[-1])
        elif "SizeMsgs" in line:
            s_msgs = (int)((line.rsplit('\n')[0]).rsplit(' ')[-1]) * INT_SIZE

        elif len(line) > 1:
            list_words = (line.rsplit('\n')[0]).rsplit('\t')
            if list_words[0] == "":
                continue

            size = s_msgs
            num = n_msgs
            idx = 0
            ppn = 4
            if n_msgs == -1 and s_msgs == -1:
                ppn = 1
                size = (int)(list_words[0]) * INT_SIZE
                num = 1
                idx = 1

            for i in range(idx, len(list_words)):
                if list_words[i] == "":
                    break
                time = (float)(list_words[i])
                time /= 2 # Nodecomm times 1 send and 1 recv
                if arch_model is None:
                    if n_procs > 16:
                        if num <= 16:
                            model.add_timing(num, size, ppn, n_procs, time)
                    else:
                        model.add_timing(num, size, ppn, time)
                else:
                    model.add_timing(arch_model, num, size, ppn, time)
                times.append(time)
                data.append([num, size, ppn])
                ppn += 1
    f.close()

    return times, data

