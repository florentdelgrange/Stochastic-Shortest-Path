SSP - Solver
===
This tool synthesises strategies for different Stochastic Shortest Path problems
in Markov Decision Processes (MDPs) following a specification of the system in the form of a ``yaml`` file.
The algorithms implemented are based on those of the article named
[*"Variation on the stochastic shortest path problem"*](https://arxiv.org/abs/1411.0835).

#### **Strategy synthesis**
  - Reachability to a subset of target states
  - Stochastic Shortest Path Expectation problem
  - Stochastic Shortest Path Percentile problem

The implementation of solvers synthesising these strategies is located in the solvers package.
