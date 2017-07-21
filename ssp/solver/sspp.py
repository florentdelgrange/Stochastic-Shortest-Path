from structures.mdp import MDP, UnfoldedMDP
from typing import List
from solver.reachability import reach
from solver import print_optimal_solution
import pulp
from numpy import resize


def force_short_paths_from(mdp: MDP, s: int, T: List[int], l: int, msg=0, solver=pulp.GLPK_CMD()):
    # First, we must define a mdp that record the length of the paths during an execution of the mdp from s
    for s in range(mdp.number_of_states):
        u_mdp = UnfoldedMDP(mdp, s, T, l)
        x = reach(u_mdp, u_mdp.target_states)
        print_optimal_solution(x, range(len(x)), u_mdp.state_name)


def build_scheduler(mdp: MDP, T: List[int], l: int, msg=0, solver=pulp.GLPK_CMD()):
    scheduler = [[None] * l for _ in range(mdp.number_of_states)]
    A = resize(-1, (mdp.number_of_states, l))
