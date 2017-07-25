from structures.mdp import MDP, UnfoldedMDP
from typing import List
from solvers.reachability import reach
import pulp
from numpy import argmax


def force_short_paths_from(mdp: MDP, s: int, T: List[int], l: int, msg=0, solver=pulp.GLPK_CMD()):
    # First, we must define a mdp that record the length of the paths during an execution of the mdp from s
    u_mdp = UnfoldedMDP(mdp, s, T, l)
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
