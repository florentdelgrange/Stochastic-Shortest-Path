import sys
import pulp

from parser.yaml_parser import import_from_yaml
from solver.reachability import reach, minimal_steps_number_to, connected_to, pr_max_1
from structures.mdp import MDP

with open(sys.argv[1], 'r') as stream:
    mdp = import_from_yaml(stream)
    print(mdp)
    #   print(minimal_steps_number_to(mdp, [1]))
    #   print(connected_to(mdp, [1]))
    #   for s in range(mdp.number_of_states):
    #       print([x for x in mdp.alpha_successors(s)])
    #   print(MDP([], [], [1, 2, 3, 4, 5], 5))
    #   for s in range(mdp.number_of_states):
    #       print(list(mdp.alpha_predecessors(s)), " -> ", s)
    #   act_max = [[] for _ in range(len(mdp._w))]
    #   print(pr_max_1(mdp, [1], act_max=act_max))
    #   print(act_max)
    scheduler = reach(mdp, [5], msg=1)
    print([mdp.state_name(s) + " -> " + mdp.act_name(scheduler(s)) for s in range(mdp.number_of_states)])
