"""
This module contains all usable functions to compute the maximum reachability probability to a set of target states
for each states of a MDP and a strategy builder such that the strategy built maximizes the probability to reach
a set of target states for each state.

Furthermore, it computes the maximum reachability probability to reach a set of target states for each state of a MDP
in a yaml file passed as argument.

Usage:

    $ python3 reachability.py <mdp-yaml> t1 t2 <...> tn

    where the arguments
        :<mdp-yaml>: the path to a yaml file that represents a MDP
        :t1 t2 <...> tn: the target states labels of the MDP
"""
import pulp
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from solvers import print_optimal_solution
from structures.mdp import MDP
from typing import List, Callable
from collections import deque

v: List[float]
"""Last optimal solution.
"""


def reach(mdp: MDP, T: List[int], msg=0, solver: pulp=pulp.GLPK_CMD()) -> List[float]:
    """
    Compute the maximum reachability probability to T for each state of the MDP in parameter and get a vector x (as list)
    such that x[s] is the maximum reachability probability to T of the state s.

    :param mdp: a MDP for which the maximum reachability probability will be computed for each of its states.
    :param T: a list of target states.
    :param msg: (optional) set this parameter to 1 to activate the debug mode in the console.
    :param solver: (optional) a LP solver allowed in puLp (e.g., GLPK or CPLEX).
    :return: the a list x such that x[s] is the maximum reachability probability to T.
    """
    states = list(range(mdp.number_of_states))
    # x[s] is the Pr^max to reach T
    x = [-1] * mdp.number_of_states
    connected = connected_to(mdp, T)

    # find all states s such that s is not connected to T
    for s in filter(lambda s: not connected[s], states):
        x[s] = 0
    # find all states s such that Pr^max to reach T is 1
    for s in pr_max_1(mdp, T, connected=connected):
        x[s] = 1

    # if there exist some other states such that Pr^max to reach T is in ]0, 1[, a LP is generated for these states
    untreated_states = list(filter(lambda s: x[s] == -1, states))
    if untreated_states:

        # formulate the LP problem
        linear_program = pulp.LpProblem("reachability", pulp.LpMinimize)
        # initialize variables
        for s in untreated_states:
            x[s] = pulp.LpVariable(mdp.state_name(s), lowBound=0, upBound=1)
        # objective function
        linear_program += sum(x)
        # constraints
        for s in untreated_states:
            for (alpha, successor_list) in mdp.alpha_successors(s):
                linear_program += x[s] >= sum(map(lambda succ_pr: succ_pr[1] * x[succ_pr[0]], successor_list))
        if msg:
            print(linear_program)

        # solve the LP
        solver.msg = msg
        linear_program.solve(solver)

        for s in untreated_states:
            x[s] = x[s].varValue

    if msg:
        print_optimal_solution(x, states, mdp.state_name)

    global v
    v = x

    return x


def build_strategy(mdp: MDP, T: List[int], solver: pulp=pulp.GLPK_CMD(), msg=0) -> Callable[[int], int]:
    """
    Build a memoryless strategy that returns the action that maximises the reachability probability to T
    of each state s in parameter of this strategy.

    :param mdp: a MDP for which the strategy will be built.
    :param T: a target states list.
    :param solver: (optional) a LP solver allowed in puLp (e.g., GLPK or CPLEX).
    :return: the strategy built.
    """
    x = reach(mdp, T, solver=solver, msg=msg)

    states = range(mdp.number_of_states)
    act_max = [[] for _ in states]

    # update act_max
    for s in filter(lambda s: not act_max[s], states):
        pr_max = 0
        for (alpha, successor_list) in mdp.alpha_successors(s):
            pr = sum(map(lambda succ_pr: succ_pr[1] * x[succ_pr[0]], successor_list))
            if pr == pr_max:
                act_max[s].append(alpha)
            elif pr > pr_max:
                pr_max = pr
                act_max[s] = [alpha]

    # compute M^max
    mdp_max = MDP([], [], mdp._w, mdp.number_of_states, validation=False)
    for s in states:
        i = 0
        for (alpha, successor_list) in mdp.alpha_successors(s):
            if alpha == act_max[s][i]:
                i += 1
                mdp_max.enable_action(s, alpha, successor_list)
            if i == len(act_max[s]):
                break

    # compute the final strategy
    minimal_steps = minimal_steps_number_to(mdp_max, T)
    strategy: List[int] = []
    for s in states:
        if x[s] == 0 or minimal_steps[s] == 0:
            strategy.append(act_max[s][0])
        else:
            for (alpha, successor_list) in mdp_max.alpha_successors(s):
                for (succ, pr) in successor_list:
                    if minimal_steps[succ] == minimal_steps[s] - 1:
                        strategy.append(alpha)
                        break
                if len(strategy) == s + 1:
                    break
    return lambda s: strategy[s]


def connected_to(mdp: MDP, T: List[int]) -> List[bool]:
    """
    Compute the states connected to T.
    For this purpose, a backward breadth-first search algorithm on the underlying graph of the MDP is used.

    :param mdp: a MDP.
    :param T: a list of target states of the MDP.
    :return: a list 'marked' such that, for each state s of the MDP, marked[s] = True if s is connected to T in
             the underlying graph of the MDP.
    """
    marked = [False] * mdp.number_of_states
    for t in T:
        marked[t] = True
    next = []
    for t in T:
        next.extend(mdp.pred(t))
    while next:
        predecessors = next
        next = []
        for pred in predecessors:
            if not marked[pred]:
                marked[pred] = True
                next.extend(mdp.pred(pred))
    return marked


def minimal_steps_number_to(mdp: MDP, T: List[int]) -> List[float]:
    """
    Compute the shortest path in term of edges in the underlying graph of the MDP to T (i.e., the minimal number of steps
    to reach T in the underlying graph). The function connected_to (a breadth first serach algorithm) is adapted to
    number the states instead of mark them.

    :param mdp: a MDP.
    :param T: a list of target states of the MDP.
    :return: a list 'steps' such that, for each state s of the MDP, steps[s] = n where n is the minimal number of steps
             to reach T in the underlying graph of the MDP.
    """
    steps = [float('inf')] * mdp.number_of_states
    for t in T:
        steps[t] = 0
    next = []
    for t in T:
        next.extend(mdp.pred(t))
    i = 1
    while next:
        predecessors = next
        next = []
        for pred in predecessors:
            if steps[pred] > i:
                steps[pred] = i
                next.extend(mdp.pred(pred))
        i += 1
    return steps


def pr_max_1(mdp: MDP, T: List[int], connected: List[bool]=[]) -> List[int]:
    """
    Compute the states s of the MDP such that the maximum probability to reach T from s is 1.

    :param mdp: a MDP.
    :param T: a target states list of the MDP.
    :param connected: (optional) list of the states of the MDP connected to T. If this parameter is not provided, it is
                      computed in the function.
    :return: the list of states s of the MDP such that the maximum probability to reach T from s is 1.
    """
    if not connected:
        connected = connected_to(mdp, T)
    removed_state = [False] * mdp.number_of_states
    in_T = [False] * mdp.number_of_states
    for t in T:
        in_T[t] = True
    disabled_action = [[False] * len(mdp.act(s))
                       for s in range(mdp.number_of_states)]
    no_disabled_actions = [0] * mdp.number_of_states

    U = [s for s in range(mdp.number_of_states) if not connected[s]]
    while len(U) > 0:
        R = deque(U)
        while len(R) > 0:
            u = R.pop()
            for (t, alpha_i) in mdp._alpha_pred[u]:
                if connected[t] and not disabled_action[t][alpha_i] and not in_T[t]:
                    disabled_action[t][alpha_i] = True
                    no_disabled_actions[t] += 1
                    if no_disabled_actions[t] == len(mdp.act(t)):
                        R.appendleft(t)
                        connected[t] = False
            removed_state[u] = True
        sub_mdp = MDP([], [], [], number_of_states=mdp.number_of_states, validation=False)
        for s in range(mdp.number_of_states):
            if not removed_state[s]:
                for alpha_i in range(len(mdp.act(s))):
                    if not disabled_action[s][alpha_i]:
                        sub_mdp.enable_action(s, mdp._enabled_actions[s][0][alpha_i],
                                              filter(lambda succ_pr: not removed_state[succ_pr[0]],
                                                     mdp._enabled_actions[s][1][alpha_i]))
        mdp = sub_mdp
        connected = connected_to(mdp, T)
        U = [s for s in range(mdp.number_of_states)
             if not connected[s] and not removed_state[s]]
    pr_1 = [s for s in range(mdp.number_of_states) if not removed_state[s]]
    return pr_1


if __name__ == '__main__':
    from io_utils import graphviz, yaml_parser

    with open(sys.argv[1], 'r') as stream:
        mdp = yaml_parser.import_from_yaml(stream)
        T = [mdp.state_index(t) for t in sys.argv[2:]]
        strategy = build_strategy(mdp, T, msg=1)
        strategy_actions = [strategy(s) for s in range(mdp.number_of_states)]
        graphviz.export_mdp(mdp, sys.argv[1].replace('.yaml', '').replace('.yml', ''), strategy_actions)
