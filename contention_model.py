from queue_model import*

class ContentionModel(Model, object):
    def add_timing(self, bytes_per_link, time):
        self.times.append(time)
        self.data.append([bytes_per_link]) # num bytes traversing each link

    def model_func(self, bytes_per_link):
        if len(self.variables) == 0:
            return 0
        print(self.variables[0], bytes_per_link)
        return self.variables[0] * bytes_per_link

class ContentionArch(object):
    network_arch = ""
    queue_arch = ""
    contention_model = ""

    def __init__(self, queue_arch, network_arch):
        self.queue_arch = queue_arch
        self.network_arch = network_arch
        self.contention_model = ContentionModel()

    def add_timing(self, n_msgs, s_msgs, ppn, n_procs, time):
        t = self.queue_arch.model_func(n_msgs, s_msgs, self.network_arch, ppn)
        self.contention_model.add_timing(s_msgs * (n_procs/2), time - t)

    def calc_model(self):
        self.contention_model.calc_model()

    def print_model(self):
        print("Network Contention: ")
        self.contention_model.print_model()

    def model_func(self, n_msgs, s_msgs, ppn, n_procs):
        t = self.queue_arch.model_func(n_msgs, s_msgs, 
                self.network_arch, ppn)
        t += self.contention_model.model_func(s_msgs * (n_procs / 2))
        return t

    def plot_model(self, times, data, n_procs, fn = None):
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
            model_data = [self.model_func(n, s, 16, n_procs) for n in xdata]
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


fn = "bw_output/model/contention/nodecomm_contention_128.out"

contention_model = ContentionArch(queue_model, network_model)
times, data = parse(fn, contention_model, n_procs = 128)
contention_model.calc_model()
contention_model.print_model()

if __name__ == '__main__':
    contention_model.plot_model(times, data, n_procs = 128, fn =
            "%s/contention.pdf"%fig_folder)
