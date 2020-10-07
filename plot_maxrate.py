from nodecomm_model import *
import pyfancyplot.plot as plot

xdata = list()
socket = list()
node = list()
network = list()
injection = list()
for s in range(18):
    size = 2**s
    xdata.append(size)
    socket.append(socket_model.model_func(1, size, 1))
    node.append(node_model.model_func(1, size, 1))
    network.append(network_model.model_func(1, size, 1))
    injection.append(network_model.model_func(1, size, 16))

plot.add_luke_options()
plot.set_palette(palette="deep")
plot.line_plot(socket, xdata, label="Socket")
plot.line_plot(node, xdata, label="Node")
plot.line_plot(network, xdata, label="Network PPN $<$ 4")
plot.line_plot(injection, xdata, label="Newtork PPN $>$ 4")
plot.set_scale("log", "log")
plot.add_anchored_legend(ncol=2)
plot.add_labels("Message Size", "Modeled Time (Seconds)")
plot.save_plot("maxrate.pdf")
