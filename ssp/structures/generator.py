"""
This module contains all functions needed to generate MDP.
"""
import random
from structures.mdp import MDP
from typing import Tuple, List


def random_MDP(n: int, a: int,
               strictly_a: bool = False,
               complete_graph: bool = False,
               weights_interval: Tuple[int, int] = (1, 1),
               force_weakly_connected_to: bool=False) -> MDP:
    """
    Generate a random MDP.

    :param n: number of states of the generated MDP.
    :param a: number of actions of the generated MDP.
    :param strictly_a: (optional) set this parameter to True to force each state of the generated MDP to have exactly
                       a actions, i.e. |A(s)| = a for all state s.
    :param complete_graph: (optional) set this parameter to True to force the MDP to have a complete underlying graph.
    :param weights_interval: (optional) set an interval (w1, w2) for weights of each action. Following this parameter,
                             w(α) ∈ [w1, w2] for each action α of the generated MDP.
    :param force_weakly_connected_to: (optional) set this parameter to True to force some random state to be absorbing
                                      states. As consequence, some states should not be connected to a target state T
                                      and more states can have a reachability probability to T < 1.
    :return: a randomly generated MDP.
    """
    states = list(range(n))
    actions = list(range(a))
    w1, w2 = weights_interval
    if not (1 <= w1 <= w2):
        raise ValueError("weights_interval (w1, w2) must be 1 <= w1 <= w2")
    w = [random.randint(w1, w2) for _ in range(a)]
    mdp = MDP([], [], w, n, validation=False)

    for s in states:
        if not strictly_a:
            alpha_list = random.sample(actions, random.randint(1, a))
        else:
            alpha_list = actions
        if complete_graph:
            successors_set = set()
        for alpha in alpha_list:
            successors = random.sample(states, random.randint(1, n))
            if force_weakly_connected_to and random.random() >= 0.7:
                    successors = [s]
            if complete_graph:
                successors_set |= set(successors)
                if alpha == alpha_list[-1]:
                    for succ in filter(lambda succ: succ not in successors_set, states):
                        successors.append(succ)
            probabilities = random_probability(len(successors))
            mdp.enable_action(s, alpha,
                              [(successors[succ], probabilities[succ]) for succ in range(len(probabilities))])

    mdp._validation = True
    return mdp


def random_probability(n: int) -> List[float]:
    """
    Get a list of length n such that each element of this list is in ]0, 1[ (or = 1 if n = 1) and such that the sum of
    all elements of this list equals 1.
    :param n: the length of the generated list.
    :return: a list of length n such that the sum of all elements of this list equals 1.
    """
    pr = [float(random.randint(1, 42)) for _ in range(n)]
    total = sum(pr)
    for i in range(n):
        pr[i] /= total
    return pr
