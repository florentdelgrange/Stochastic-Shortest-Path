import pulp

from solver import print_optimal_solution
from solver.reachability import reach
from structures.mdp import MDP
from typing import List


def min_expected_cost(mdp: MDP, T: List[int], msg=0, solver=pulp.GLPK_CMD()):
    states = range(mdp.number_of_states)
    x = [-1 for _ in states]
    expect_inf = [False for _ in states]
    pr_reach = reach(mdp, T, msg=msg, solver=solver)
    for t in T:
        x[t] = 0
    for s in states:
        if pr_reach[s] != 1:
            x[s] = float('inf')
            expect_inf[s] = True

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
    linear_program.solve(solver)

    for s in states:
        if x[s] != 0 and x[s] != float('inf'):
            x[s] = x[s].varValue

    if msg:
        print_optimal_solution(x, states, mdp.state_name)

    return x
