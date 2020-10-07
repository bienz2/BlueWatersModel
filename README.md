## Output Data from Blue Waters Benchmarks
This repo contains output from simple benchmarks on Blue Waters supercomputer, measuring ping-pong timings on various send and recv processes (intra-socket, inter-socket, and inter-node).  It also measures the cost of splitting data across multiple processes per node.

## Performance Models
The python plots calculate performance model parameters for the max-rate model, split into intra-socket, inter-socket, and inter-node.  The scripts also calculate the affect of queue search times when receiving multiple messages, and calculate a rough estimate of network contention based on message length and distance between sending and receiving processes.
