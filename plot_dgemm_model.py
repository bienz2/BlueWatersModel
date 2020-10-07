import numpy as np
import sys
sys.path.append("../PyFancyPlots")
import plot
from nodecomm_model import *

PPN = 16
net_alpha_s = network_model.short_model.variables[0]
net_alpha_e = network_model.eager_model.variables[0]
net_alpha_r = network_model.rend_model.variables[0]
net_beta_s = network_model.short_model.variables[1]
net_beta_e = network_model.eager_model.variables[1]
net_beta_r = network_model.rend_model.variables[1]
net_beta_r_N = network_model.rend_model.variables[2][0]

node_alpha_s = node_model.short_model.variables[0]
node_alpha_e = node_model.eager_model.variables[0]
node_alpha_r = node_model.rend_model.variables[0]
node_beta_s = node_model.short_model.variables[1]
node_beta_e = node_model.eager_model.variables[1]
node_beta_r = node_model.rend_model.variables[1]

def net_model(n, s, s_N):
    if s < short_cutoff:
        return net_alpha_s * n + net_beta_s * s
    elif s < eager_cutoff:
        return net_alpha_e * n + net_beta_e * s
    else:
        beta = net_beta_r * s
        beta_N = net_beta_r_N * s_N
        if beta > beta_N:
            return net_alpha_r * n + beta
        return net_alpha_r * n + beta_N

def node_model(n, s):
    if s < short_cutoff:
        return node_alpha_s * n + node_beta_s * s
    elif s < eager_cutoff:
        return node_alpha_e * n + node_beta_e * s
    else:
        return node_alpha_r * n + node_beta_r * s


def standard_comm(N, M, K, np):
    n = (N*M) / np
    m = (M*K) / np
    iter_num = 2
    iter_size = n+m
    iter_node_size = 4*(n+m)
    T_iter = net_model(iter_num, iter_size, iter_node_size)
    T = T_iter * np;
    return T

def nap_comm(N, M, K, np):
    n = (N*M) / np
    m = (M*K) / np
    on_iter_num = 2
    on_iter_size = n+m
    T_on_iter = node_model(on_iter_num, on_iter_size)
    off_iter_num = 2
    off_iter_size = n+m
    off_iter_node_size = off_iter_size * PPN
    T_off_iter = net_model(off_iter_num, off_iter_size, off_iter_node_size)
    T_iter = (PPN-1)*T_on_iter + T_off_iter
    T = T_iter * (np / PPN)
    return T

def smart_nap_comm(N, M, K, np):
    n = (N*M) / np
    m = (M*K) / np
    on_iter_num = 2
    on_iter_size = n+m
    T_on_iter = node_model(on_iter_num, on_iter_size)
    off_iter_num = 1
    off_iter_size = max(2*n, 2*m)
    off_iter_node_size = off_iter_size * PPN
    off_iter_num_l = 2
    off_iter_size_l = n+m
    T_off_iter = net_model(off_iter_num, off_iter_size, off_iter_node_size)
    T_off_iter_l = node_model(off_iter_num_l, off_iter_size_l)
    T_iter = (PPN-1)*T_on_iter + T_off_iter + T_off_iter_l
    T = T_iter * (np / PPN)
    return T

np = 8192
n = 10
while (n < 100000):
    print(n, standard_comm(n,n,n,np), nap_comm(n,n,n,np))
    n *= 10

