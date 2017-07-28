"""
This module contains all the usable functions that concern the Stochastic Shortest Path Expectation problem to a
target set in a MDP.

Furthermore, this module computes the minimum expected length of paths to a target set T from each states of a MDP.

Usage:

    $ python3 sspe.py <mdp-yaml> t1 t2 <...> tn

    where the arguments
        :<mdp-yaml>: the path to a yaml file that represents a MDP
        :t1 t2 <...> tn: the target states of the MDP
"""
import pulp
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from solvers import print_optimal_solution
from solvers.reachability import pr_max_1
from structures.mdp import MDP
from typing import List, Callable
from numpy import argmin


def min_expected_cost(mdp: MDP, T: List[int], msg=0, solver: pulp = pulp.GLPK_CMD()) -> List[float]:
    """
    Compute the minimum expected length of paths to the set of targets T from each state in the MDP.

    :param mdp: a MDP.
    :param T: a list of target states of the MDP.
    :param msg: (optional) set this parameter to 1 to activate the debug mode in the console.
    :param solver: (optional) a LP solver allowed in puLp (e.g., GLPK or CPLEX).
    :return: a list x such that x[s] is the mimum expected length of paths to the set of targets T from the state s of
             the MDP.
    """
    states = range(mdp.number_of_states)
    x = [float('inf')] * mdp.number_of_states
    expect_inf = [True] * mdp.number_of_states

    # determine states for which x[s] != inf
    for s in pr_max_1(mdp, T):
        x[s] = -1
        expect_inf[s] = False
    for t in T:
        x[t] = 0

    # formulate the LP problem
    linear_program = pulp.LpProblem("minimum expected length of path to target", pulp.LpMaximize)
    # initialize variables
    for s in filter(lambda s: x[s] == -1, states):
        x[s] = pulp.LpVariable(mdp.state_name(s), lowBound=0)
    # objective function
    linear_program += sum(map(lambda s: x[s], filter(lambda s: not expect_inf[s], states)))
    # constraints
    for s in filter(lambda s: x[s] == -1, states):
        for (alpha, successor_list) in mdp.alpha_successors(s):
            if not list(filter(lambda succ_pr: expect_inf[succ_pr[0]], successor_list)):
                linear_program += x[s] <= mdp.w(alpha) + sum(
                    map(lambda succ_pr: succ_pr[1] * x[succ_pr[0]], successor_list))
    if msg:
        print(linear_program)

    # solve the LP
    solver.msg = msg
    if linear_program.variables():
        linear_program.solve(solver)

    for s in states:
        if x[s] != 0 and x[s] != float('inf'):
            x[s] = x[s].varValue

    if msg:
        print_optimal_solution(x, states, mdp.state_name)

    return x


def build_scheduler(mdp: MDP, T: List[int], solver: pulp = pulp.GLPK_CMD()) -> Callable[[int], int]:
    """
    Build a memoryless scheduler that returns, following a state s of the MDP, the action that minimize
    the expected length of paths to a set of target states T.

    :param mdp: a MDP for which the scheduler will be built.
    :param T: a target states list.
    :param solver: (optional) a LP solver allowed in puLp (e.g., GLPK or CPLEX).
    :return: the scheduler built.
    """
    x = min_expected_cost(mdp, T, solver=solver)

    states = range(mdp.number_of_states)
    act_min = [
        mdp.act(s)[argmin(
            [mdp.w(alpha) * sum(
                map(lambda succ_pr: succ_pr[1] * x[succ_pr[0]], succ_list)
            ) for (alpha, succ_list) in mdp.alpha_successors(s)]
        )]
        for s in states
    ]

    return lambda s: act_min[s]


if __name__ == '__main__':
    from io_utils import yaml_parser, graphviz

    with open(sys.argv[1], 'r') as stream:
        mdp = yaml_parser.import_from_yaml(stream)
        graphviz.export_mdp(mdp, sys.argv[1].replace('.yaml', '').replace('.yml', ''))
        T = [int(t) for t in sys.argv[2:]]
        min_expected_cost(mdp, T, msg=1)
