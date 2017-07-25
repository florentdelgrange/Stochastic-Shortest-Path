import random
import numpy.random # numpy.random excludes the highest value, contrary to classic random python module
from structures.mdp import MDP
from typing import Tuple, List


def random_MDP(n: int, a: int,
               strictly_a: bool=False, complete_graph: bool=False,
               weights_interval: Tuple[int, int]=(1, 1)) -> MDP:
    states = list(range(n))
    actions = list(range(a))
    w1, w2 = weights_interval
    if not (1 <= w1 <= w2):
        raise RuntimeError("weights_interval (w1, w2) must be 1 <= w1 <= w2")
    w = [random.randint(w1, w2) for _ in range(a)]
    mdp = MDP([], [], w, n)

    for s in states:
        if not strictly_a:
            alpha_list = random.sample(actions, random.randint(1, a))
        else:
            alpha_list = actions
        if complete_graph:
            successors_set = set()
        for alpha in alpha_list:
            successors = random.sample(states, random.randint(1, n))
            if complete_graph:
                successors_set | set(successors)
                if alpha == alpha_list[-1]:
                    for succ in filter(lambda succ: succ not in successors_set, states):
                        successors.append(succ)
            probabilities = random_probability(len(successors))
            mdp.enable_action(s, alpha,
                              [(successors[succ], probabilities[succ]) for succ in range(len(successors))])

    return mdp


def random_probability(n: int) -> List[float]:
    pr = []
    current = 1
    for _ in range(n - 1):
        next_pr = 0.
        while not next_pr:
            next_pr = numpy.random.uniform(0, current)
        pr.append(next_pr)
        current -= next_pr
    pr.append(current)
    return pr
