import numpy as np
import pyfancyplot.plot as plot
from nodecomm_model import *

PPN = 16
sizes = [1, 256, 4096, 65536]
num_procs = [256, 4096, 65536]

rd_costs = list()
smp_costs = list()
nap_costs = list()

size = 8
addcost = 0.115543 / (80000000.0)

intra_cost = node_model.model_func(1, size, PPN)
inter_cost = network_model.model_func(1, size, PPN)
smp_cost = network_model.model_func(1, size, 1)
flop_cost = addcost*size

rd_costs.append(list())
smp_costs.append(list())
nap_costs.append(list())

plot.set_palette(palette='deep', n_colors = 3)

for s in range(7, 17):
    n_procs = 2**s
    num_nodes = n_procs/PPN
    intra_steps = np.log2(PPN)
    inter_steps = np.log2(num_nodes)
    flop_steps = np.log2(n_procs)
    cost = intra_cost * intra_steps + inter_cost * inter_steps + flop_steps*flop_cost
    rd_costs[-1].append(cost)

    cost = intra_cost*(2*intra_steps) + smp_cost*inter_steps + flop_steps*flop_cost
    smp_costs[-1].append(cost)

    inter_steps = np.ceil(np.log2(num_nodes) / np.log2(16))
    intra_steps = np.log2(n_procs) 
    flop_steps += np.log2(PPN)
    cost = intra_cost*intra_steps + inter_cost * inter_steps + flop_steps*flop_cost
    print(intra_cost, intra_steps, inter_cost, inter_steps)
    nap_costs[-1].append(cost)


plot.line_plot(rd_costs[-1], label = "RD")
plot.line_plot(smp_costs[-1], label = "SMP")
plot.line_plot(nap_costs[-1], label = "NAP")
plot.add_anchored_legend(ncol=3)
loc, lbl = plot.plt.xticks()
plot.set_xticks(loc[1:-1], [(int)((2**(i+7))) for i in loc[1:-1]])
plot.add_labels("Number of Processes", "Modeled Time (Seconds)")
plot.save_plot("model_coll_scale.pdf")




n_procs = 32768

rd_costs.append(list())
smp_costs.append(list())
nap_costs.append(list())

plot.set_palette(palette='deep', n_colors = 3)

for s in range(12):
    size = 8*(2**s)
    flop_cost = addcost*size

    intra_cost = node_model.model_func(1, size, PPN)
    inter_cost = network_model.model_func(1, size, PPN)
    smp_cost = network_model.model_func(1, size, 1)

    num_nodes = n_procs/PPN
    intra_steps = np.log2(PPN)
    inter_steps = np.log2(num_nodes)
    flop_steps = np.log2(n_procs)    
    cost = intra_cost * intra_steps + inter_cost * inter_steps + flop_steps*flop_cost
    rd_costs[-1].append(cost)

    cost = intra_cost*(2*intra_steps) + smp_cost*inter_steps + flop_steps*flop_cost
    smp_costs[-1].append(cost)

    inter_steps = np.ceil(np.log2(num_nodes) / np.log2(16))
    intra_steps = np.log2(n_procs) 
    flop_steps += np.log2(PPN)    
    cost = intra_cost*intra_steps + inter_cost * inter_steps + flop_steps*flop_cost
    nap_costs[-1].append(cost)


plot.line_plot(rd_costs[-1], label = "RD")
plot.line_plot(smp_costs[-1], label = "SMP")
plot.line_plot(nap_costs[-1], label = "NAP")
plot.add_anchored_legend(ncol=3)
loc, lbls = plot.plt.xticks()
plot.add_labels("Reduction Size (Bytes)", "Modeled Time (Seconds)")
plot.set_scale('linear', 'log')
plot.set_xticks(loc[1:-1], [(int)(8*(2**i)) for i in loc[1:-1]])
plot.save_plot("model_coll_size.pdf")


