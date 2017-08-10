"""
This module contains all the usable functions that concern the Stochastic Shortest Path Percentile problem to a
target set in a MDP.

Furthermore, this module computes the maximum probability to reach T from a state s0 of a MDP with path length
inferior than a threshold l.
The module decides if there exists a strategy such that Pr_s0 ({ π ∈ Paths(s0) | TS^T(π) <= l }) >= α. If this is true,
it plots with graphviz the unfolded MDP and shows in red the actions chosen by the optimal strategy
that solves this problem.

Usage:

    $ python3 sspp.py <mdp-yaml> s0 l b t1 t2 <...> tn

    where the arguments are
        :<mdp-yaml>: the path to a yaml file that represents a MDP
        :s0 : the initial state label
        :l : the paths length threshold
        :b : the probability threshold
        :t1 t2 <...> tn: the target states label of the MDP
"""

import pulp
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import solvers.reachability
from structures.mdp import MDP, UnfoldedMDP
from typing import List
from io_utils import graphviz, yaml_parser

unfolded_mdp_name = 'unfolded_mdp'


def force_short_paths_from(mdp: MDP, s: int, T: List[int], l: int, b: float, msg=0, solver=pulp.GLPK_CMD()):
    """
    Compute the maximum probability to reach a set of target states T from a state s of a MDP with a path length
    inferior than a threshold l and get the strategy on the unfolded mdp.

    :param mdp: a MDP.
    :param s: the state for which the probability to reach T is computed.
    :param T: a set of target states of the MDP.
    :param l: the paths length threshold.
    :param b: probability threshold.
    :param msg: (optional) set this parameter to 1 to activate the debug mode in the console.
    :param solver: (optional) a LP solver allowed in puLp (e.g., GLPK or CPLEX).
    :return: the unfolded MDP from s and the strategy that solve the reachability problem for the unfolded MDP from s.
             Note that the strategy uses the index of states of the unfolded MDP and not the (s, v) format.
    """
    if not (0. <= b <= 1.):
        raise ValueError("alpha must be a probability threshold, i.e., 0 <= alpha <= 1 (current value : %g)." % alpha)
    # First, we must define a mdp that record the length of the paths during an execution of the mdp from s
    u_mdp = UnfoldedMDP(mdp, s, T, l)
    strategy = solvers.reachability.build_strategy(u_mdp, u_mdp.target_states, msg=msg, solver=solver)
    if solvers.reachability.v[0] >= b:
        return u_mdp, strategy
    else:
        return u_mdp, None


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as stream:
        mdp = yaml_parser.import_from_yaml(stream)
        s0 = int(mdp.state_index(sys.argv[2]))
        l = int(sys.argv[3])
        b = float(sys.argv[4])
        T = [mdp.state_index(t) for t in sys.argv[5:]]
        u_mdp, strategy = force_short_paths_from(mdp, s0, T, l, b, msg=1)
        if not strategy:
            print("There don't exist any strategy that solve the SSPP problem for this MDP from the state %s to {%s} "
                  "and the probability threshold %g." % (sys.argv[2], ", ".join(sys.argv[5:]), b))
        else:
            graphviz.export_mdp(u_mdp, sys.argv[1].replace('.yaml', '').replace('.yml', ''),
                                [strategy(s) for s in range(u_mdp.number_of_states)])
