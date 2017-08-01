"""
This module contains all the usable functions that concern the Stochastic Shortest Path Percentile problem to a
target set in a MDP.

Furthermore, this module computes the maximum probability to reach T from a state s0 of a MDP with path length
inferior than a threshold l. The module plot with graphviz the unfolded MDP used to compute this probability.

Usage:

    $ python3 sspp.py <mdp-yaml> l s0 t1 t2 <...> tn

    where the arguments
        :<mdp-yaml>: the path to a yaml file that represents a MDP
        :l : the paths length threshold
        :s0 : the initial state
        :t1 t2 <...> tn: the target states of the MDP
"""

import pulp
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import solvers.reachability
from structures.mdp import MDP, UnfoldedMDP
from typing import List
from solvers.reachability import reach
from numpy import argmax
from io_utils import graphviz, yaml_parser

unfolded_mdp_name = 'unfolded_mdp'


def force_short_paths_from(mdp: MDP, s: int, T: List[int], l: int, msg=0, viz: bool = False, solver=pulp.GLPK_CMD()):
    """
    Compute the maximum probability to reach a set of target states T from a state s of a MDP with a path length
    inferior than a threshold l.

    :param mdp: a MDP.
    :param s: the state for which the probability to reach T is computed.
    :param T: a set of target states of the MDP.
    :param l: the paths length threshold.
    :param msg: (optional) set this parameter to 1 to activate the debug mode in the console.
    :param viz: (optional) set this parameter to True to vizualize with graphviz the unfolded MDP used to compute the
                probability.
    :param solver: (optional) a LP solver allowed in puLp (e.g., GLPK or CPLEX).
    :return: the maximum probability to reach the set of target states T from the state s of the MDP with a path length
             inferior than l
    """
    # First, we must define a mdp that record the length of the paths during an execution of the mdp from s
    u_mdp = UnfoldedMDP(mdp, s, T, l)
    if viz:
        graphviz.export_mdp(u_mdp, unfolded_mdp_name)
    return reach(u_mdp, u_mdp.target_states, msg=msg, solver=solver)


def build_scheduler(mdp: MDP, T: List[int], l: int, msg=0, solver=pulp.GLPK_CMD()):
    """
    Build a scheduler that returns, following a state s of a MDP and a path length v, the maximum probability to reach
    T with a path length inferior than l from s, knowing that the length of the path to reach s is currently v.

    :param mdp: a MDP.
    :param T: a set of target states of the MDP.
    :param l: the paths length threshold.
    :param msg: (optional) set this parameter to 1 to activate the debug mode in the console.
    :param solver: (optional) a LP solver allowed in puLp (e.g., GLPK, CPLEX, etc.).
    :return: the scheduler built.
    """
    # this matrix contains all the optimal solutions such that V[s][v] is the optimal solution for the state (s, v) in
    # the unfolded MDP.
    V = [[- 1] * (l + 1) for _ in range(mdp.number_of_states)]

    def x(s: int, v: int):
        """
        Get the optimal solution if it is already computed, compute it otherwise.

        :param s: a state s of the MDP.
        :param v: length of the currently computed path in the unfolded MDP.
        :return: the optimal solution of the state (s, v) in the unfolded MDP, i.e., the maximum probability to reach
                 T* = { (t, v) | t ∈ T and v <= l } from (s, v) in the unfolded mdp.
        """
        if v > l:
            return 0
        elif V[s][v] == -1:
            u_mdp = UnfoldedMDP(mdp, s, T, l, v)
            x = [V[s][v] for (s, v) in map(u_mdp.convert, range(u_mdp.number_of_states - 1))]
            x.append(-1)
            x = reach(u_mdp, u_mdp.target_states, msg=msg, solver=solver, v=x)
            for i in range(u_mdp.number_of_states - 1):
                (s, v) = u_mdp.convert(i)
                V[s][v] = x[i]
        return V[s][v]

    def scheduler(s, v):
        # V[s][v] computation if it is not already done
        x(s, v)
        return argmax(
            [sum(
                map(lambda succ_pr: succ_pr[1] * x(succ_pr[0], v + mdp.w(alpha)), succ_list)
            ) for (alpha, succ_list) in mdp.alpha_successors(s)]
        )

    return scheduler


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as stream:
        mdp = yaml_parser.import_from_yaml(stream)
        l = int(sys.argv[2])
        s0 = int(mdp.state_index(sys.argv[3]))
        T = [mdp.state_index(t) for t in sys.argv[4:]]
        u_mdp = UnfoldedMDP(mdp, s0, T, l)
        T2 = u_mdp.target_states
        scheduler = solvers.reachability.build_scheduler(u_mdp, T2, msg=1)
        scheduler_actions = [scheduler(s) for s in range(u_mdp.number_of_states)]
        graphviz.export_mdp(u_mdp, sys.argv[1].replace('.yaml', '').replace('.yml', ''), scheduler_actions)
