SSP Solver
===
*Markov decision processes* (MDPs) are stochastic systems widely used to model both stochastic and nondeterministic situations, requiring to optimise cost to achieve a goal (e.g., an agent interacting with its environment).
An MDP consists of states, actions and probability distributions formed by the current state of the system and the action selected.
*Strategies* for MDPs prescribe which actions to choose in each state, according to or not the previously visited states in the system.

SSP Solver is a tool written in `python3` that synthesises strategies for different Stochastic Shortest Path problems
in MDPs following a specification of the system in the form of a ``yaml`` file.
The algorithms implemented are based on those presented in ["Variation on the stochastic shortest path problem"](https://arxiv.org/abs/1411.0835).

## Setup
SSP Solver has many [dependencies](https://github.com/theGreatGiorgio/Stochastic-Shortest-Path/blob/master/ssp/requirements.txt) and you can install them with pip:
```pip3 install -r requirements.txt```

Note that GLPK is also required.

## System specification
You can encode your systems in a `yaml` file with the following syntax:
```yaml
mdp:
  states:
    # for each state s of the system
    - name: <name of a state s>
      enabled actions:
        # for each enabled action α of the state s
        - name: <name of an enabled action α of s>
          transitions:
            # for each transition s ➞ α ➞ s'
            - target: <name of an α-successor s' of s>
              probability: <probability to go from s to s' by choosing α>
  actions:
    # for each action in the system
    - name: <name of an action α>
      weight: <weight of α> # strictly positive weight
```
You can find some examples [here](https://github.com/theGreatGiorgio/Stochastic-Shortest-Path/tree/master/ssp/examples).
### Example
Consider the following MDP:
![alt text](https://cdn.rawgit.com/theGreatGiorgio/Stochastic-Shortest-Path/95e87948/ssp/examples/mdp2.eps)
This MDP can be encoded as a yaml as [here](https://github.com/theGreatGiorgio/Stochastic-Shortest-Path/blob/master/ssp/examples/mdp2.yaml).

## Strategy synthesis
The MDPs are in a configuration where actions have strictly positive costs.
The solver is able to synthesise strategies maximising the
  - probability to reach a set of target states (reachability problem)
  - expected cost of reaching a set of target states (Stochastic Shortest Path Expectation problem)
  - probability to reach a set of target states with a cost bounded (Stochastic Shortest Path Percentile problem)

The algorithms synthesising these strategies make use of *linear programming*.
### Reachability problem
The reachability solver allows to synthesise a strategy maximising the probability to reach a subset a target states.
#### Usage
```
python3 solvers/reachability.py <yaml_file> t1 t2 ... tn
```
where T = \{t1, t1, ..., tn\} is the set of target states.

#### Example

For example, consider our [example MDP](https://github.com/theGreatGiorgio/Stochastic-Shortest-Path/blob/master/ssp/examples/mdp2.yaml), we are interested in synthesising a strategy that maximises the probability to reach the state v.
We run
```
python3 solvers/reachability.py examples/mdp2.yaml v
```
The output is the **values** for each state, i.e., the max. probability to reach the target states:
```
Optimal solution :
v[s] = 0.0568182 	 v[t] =         0
v[u] =     0.125 	 v[v] =         1
v[w] = 0.0454545 	 v[x] =         0
v[y] =         0
```
Moreover, a representation of the strategy (showed in red) is generated:
![alt text](https://cdn.rawgit.com/theGreatGiorgio/Stochastic-Shortest-Path/d4282048/ssp/examples/mdp2.gv.pdf)

### Stochastic shortest path: Expectation problem
The sspe solver allows to synthesise a strategy minimising the expected cost to a subset of target states

#### Usage
```
python3 solvers/sspe.py <yaml_file> t1 t2 ... tn
```
where T = \{t1, t1, ..., tn\} is the set of target states.
#### Example
For example, consider our [example MDP](https://github.com/theGreatGiorgio/Stochastic-Shortest-Path/blob/master/ssp/examples/mdp2.yaml), we are interested in synthesising a strategy that minimises the expectation to reach the state t.
We run
```
python3 solvers/sspe.py examples/mdp2.yaml t
```
The output is the **values** for each state, i.e., the min. expected cost to reach the target states:
```
Optimal solution :
v[s] =   19 	 v[t] =    0
v[u] =   24 	 v[v] =  inf
v[w] =   24 	 v[x] =  inf
v[y] =  inf
```
Moreover, a representation of the strategy (showed in red) is generated:
![alt text](https://cdn.rawgit.com/theGreatGiorgio/Stochastic-Shortest-Path/182f3eb0/ssp/examples/mdp2-e.gv.pdf)

### Stochastic shortest path: percentile Problem
The sspp solver allows to synthesise a strategy maximising the probability to reach a subset of target states from a given state with a fixed cost bounded.
#### Usage
```
python3 solvers/sspp.py <yaml_file> s0 l b t1 t2 ... tn
```
where s0 is the initial state, l is the cost threshold, b is the probability threshold and T = \{t1, t2, ..., tn\} is the set of target states.
Thus, the strategy synthesised satisfies Prmax(s0 ⊨ ♢T | cost of paths <= l) >= b. Note that if you don't want to involve the probability threshold b into the synthesis, just set it to 0.

#### Example
For example, consider the following MDP.
![alt text](https://cdn.rawgit.com/theGreatGiorgio/Stochastic-Shortest-Path/182f3eb0/Rapport/figures/sspp1.eps)
We are interested in synthesising a strategy that maximises the probability to reach the state t within a cost of 8 from the state s.
We run
```
python3 solvers/sspp.py examples/simple_mdp.yaml s 8 0 t
```
The output is the **values** for each state, i.e., the max. probability to reach the target states within a cost of 8:
```
v[(s, 0)] = 0.75 	 v[(t, 3)] =    1
v[(u, 3)] =  0.5 	 v[(u, 8)] =    0
v[(s, 5)] =  0.5 	 v[(t, 8)] =    1
v[⊥]      =    0
```
Note that each state considered by the strategy is a tuple formed by the current state of the system and the current cost of the paths. The state ⊥ represents the state for which the cost of the current path has exceeded 8. That means that the strategy records the current cost of paths of the execution.
A representation of the strategy (showed in red) is then generated:
![alt text](https://cdn.rawgit.com/theGreatGiorgio/Stochastic-Shortest-Path/182f3eb0/Rapport/figures/simple_mdp2.pdf)
