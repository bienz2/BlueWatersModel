from nodecomm_model import *

class QueueModel(Model, object):
    def add_timing(self, n_msgs, time):
        self.times.append(time)
        self.data.append([n_msgs**2])

    def model_func(self, n_msgs):
        if len(self.variables) == 0:
            return 0
        return self.variables[0] * (n_msgs**2)

class QueueArch(object):
    queue_model = ""

    def __init__(self):
        self.queue_model = QueueModel()

    def add_timing(self, standard_arch, n_msgs, s_msgs, ppn, time):
        t = standard_arch.model_func(n_msgs, s_msgs, ppn)
        self.queue_model.add_timing(n_msgs, time - t)

    def calc_model(self):
        self.queue_model.calc_model()

    def print_model(self):
        print("Queue Search: ")
        self.queue_model.print_model()

    def model_func(self, n_msgs, s_msgs, arch_model, ppn):
        t = arch_model.model_func(n_msgs, s_msgs, ppn)
        t += self.queue_model.model_func(n_msgs)
        return t

    def plot_model(self, times, data, arch_model, fn = None):
        msg_sizes = [d[1] for d in data]
        msg_nums = [d[0] for d in data]
        model_sizes = sorted(list(set(msg_sizes)))
        model_nums = sorted(list(set(msg_nums)))

        msg_time_s = list()
        msg_data_s = list()
        msg_time_e = list()
        msg_data_e = list()
        msg_time_r = list()
        msg_data_r = list()
        for s in model_sizes:
            msg_data_s.append(list())
            msg_time_s.append(list())
            msg_data_e.append(list())
            msg_time_e.append(list())
            msg_data_r.append(list())
            msg_time_r.append(list())

        m = ""
        for i in range(len(msg_sizes)):
            s = msg_sizes[i]
            idx = model_sizes.index(s)
            if s / msg_nums[i] < short_cutoff:
                d = msg_data_s[idx]
                t = msg_time_s[idx]
            elif s / msg_nums[i] < eager_cutoff:
                d = msg_data_e[idx]
                t = msg_time_e[idx]
            else:
                d = msg_data_r[idx]
                t = msg_time_r[idx]
            d.append(msg_nums[i])
            t.append(times[i])

        colors = plot.sns.color_palette(n_colors = len(model_sizes))

        ctr = 0
        for i in range(2, len(model_sizes), 2):
            plot.add_luke_options()
            plot.set_scale('log', 'log')
            plot.set_xlim(1e0, 1e5)
            plot.set_ylim(1e-6, 1e1)

            s = model_sizes[i]
            msg_data = msg_data_s[i] + msg_data_r[i] + msg_data_e[i]
            xdata = sorted(list(set(msg_data)))
            model_data = [self.model_func(n, s, arch_model, 16) for n in xdata]
            plot.line_plot(model_data, xdata, color = colors[ctr], label = "%d Bytes"%s)
            plot.scatter_plot(msg_data_s[i], msg_time_s[i], color = colors[ctr],
                    marker='o', s = [20*4]*len(msg_data_s[i]))
            plot.scatter_plot(msg_data_e[i], msg_time_e[i], color = colors[ctr],
                    marker='*', s = [20*4]*len(msg_data_e[i]))
            plot.scatter_plot(msg_data_r[i], msg_time_r[i], color = colors[ctr],
                    marker='.', s = [20*4]*len(msg_data_r[i]))
            ctr += 1

            plot.set_scale('log', 'log')
            plot.set_xlim(1e0, 1e5)
            plot.set_ylim(1e-6, 1e1)
            plot.add_anchored_legend(ncol = 3,
                            anchor = (0., 1.20, 1.,.102))

        plot.add_labels("Number of Messages Communicated", "Time (seconds)")
        if fn:
            plot.save_plot("%s"%fn)
        else:
            plot.display_plot()



names = ["node_queue", "node_queue_min"]
fn = "bw_output/model/queue_search/%s"

n_msgs = 0
s_msgs = 0

queue_models = list()
times = list()
data = list()
for i in range(len(names)):
    queue_models.append(QueueArch())
    time_list, data_list = parse(fn%names[i], queue_models[i], node_model)
    times.append(time_list)
    data.append(data_list)
    queue_models[i].calc_model()
    queue_models[i].print_model()


queue_model = QueueArch()
for i in range(len(names)):
    time_list, data_list = parse(fn%names[i], queue_model, node_model)
    break
queue_model.calc_model()
queue_model.print_model()

if __name__ == '__main__':
    for i in range(len(names)):
        t = times[i]
        d = data[i]
        queue_models[i].plot_model(t, d, node_model, "%s/%s.pdf"%(fig_folder, names[i]))


    

