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


def min_expected_cost(mdp: MDP, T: List[int], msg=0, solver: pulp=pulp.GLPK_CMD()) -> List[float]:
    states = range(mdp.number_of_states)
    x = [float('inf')] * mdp.number_of_states
    expect_inf = [True] * mdp.number_of_states
    pr_reach = pr_max_1(mdp, T)
    for s in pr_reach:
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
    linear_program += sum(filter(lambda x_s: x_s != float('inf'), x))
    # constraints
    for s in filter(lambda s: x[s] != 0 and x[s] != float('inf'), states):
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


def build_scheduler(mdp: MDP, T: List[int], solver: pulp=pulp.GLPK_CMD()) -> Callable[[int], int]:
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
        graphviz.export_mdp(mdp, 'mdp')
        T = [int(t) for t in sys.argv[2:]]
        min_expected_cost(mdp, T, msg=1)
