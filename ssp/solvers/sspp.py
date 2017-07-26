import pulp
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from structures.mdp import MDP, UnfoldedMDP
from typing import List
from solvers.reachability import reach
from numpy import argmax
from io_utils import graphviz, yaml_parser

unfolded_mdp_name = 'unfolded_mdp'


def force_short_paths_from(mdp: MDP, s: int, T: List[int], l: int, msg=0, viz: bool = False, solver=pulp.GLPK_CMD()):
    # First, we must define a mdp that record the length of the paths during an execution of the mdp from s
    u_mdp = UnfoldedMDP(mdp, s, T, l)
    if viz:
        graphviz.export_mdp(u_mdp, unfolded_mdp_name)
    return reach(u_mdp, u_mdp.target_states, msg=msg, solver=solver)


def build_scheduler(mdp: MDP, T: List[int], l: int, msg=0, solver=pulp.GLPK_CMD()):
    V = [[- 1] * (l + 1) for _ in range(mdp.number_of_states)]

    def x(s: int, v: int):
        if V[s][v] == -1:
            u_mdp = UnfoldedMDP(mdp, s, T, l, v)
            x = [V[s][v] for (s, v) in map(u_mdp.convert, range(u_mdp.number_of_states - 1))]
            x.append(-1)
            x = reach(u_mdp, u_mdp.target_states, msg=1, solver=solver, v=x)
            for i in range(u_mdp.number_of_states - 1):
                (s, v) = u_mdp.convert(i)
                V[s][v] = x[i]
        return V[s][v]

    def scheduler(s, v):
        # V[s][v] initialization
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
        mdp_name = sys.argv[1].replace('.yaml', '').replace('.yml', '')
        graphviz.export_mdp(mdp, mdp_name)
        unfolded_mdp_name = mdp_name + ' (unfolded)'
        l = int(sys.argv[2])
        s0 = int(sys.argv[3])
        T = [int(t) for t in sys.argv[4:]]
        force_short_paths_from(mdp, s0, T, l, msg=1, viz=True)
