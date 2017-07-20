from structures.mdp import MDP, UnfoldedMDP
from typing import List
from solver.reachability import reach
import pulp


def force_short_paths_from(mdp: MDP, s: int, T: List[int], l: int, msg=0, solver=pulp.GLPK_CMD()):
    # First, we must define a mdp that record the length of the paths during an execution of the mdp from s
    u_mdp = UnfoldedMDP(mdp, s, T, l)
    reach(u_mdp, u_mdp.target_states, msg, solver)


