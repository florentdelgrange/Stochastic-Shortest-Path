"""
This module contains all functions needed to generate MDP.
Usage :

    $ python3 generator.py N M

    where the arguments are :
        :N : the number of states of the generated MDP
        :M : the number of actions of the generated MDP

    options:
        --strictly-A : force each state of the generated MDP to have exactly M actions, i.e. |A(s)| = a for all state s.
        --complete-graph : force the MDP to have a complete underlying graph.
        --complete-mdp : create a non-random complete MDP.
        --weak : force some random state to be absorbing states. As consequence, some states should not be connected to
                 a target state T.
        --weights w1 w1: set an interval (w1, w2) for weights of each action. Following this parameter,
                         w(α) ∈ [w1, w2] for each action α of the generated MDP.
        -o <filename>: output file name (create the file if provided).
        --viz : graphviz plot


"""
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import random
from structures.mdp import MDP
from typing import Tuple, List
from io_utils import yaml_parser, graphviz


def random_MDP(n: int, a: int,
               strictly_A: bool = False,
               complete_graph: bool = False,
               weights_interval: Tuple[int, int] = (1, 1),
               force_weakly_connected_to: bool=False) -> MDP:
    """
    Generate a random MDP.

    :param n: number of states of the generated MDP.
    :param a: number of actions of the generated MDP.
    :param strictly_A: (optional) set this parameter to True to force each state of the generated MDP to have exactly
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
    mdp = MDP([], [], w, n)

    for s in states:
        if not strictly_A:
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


def complete_MDP(n: int, a: int, w: List[int]=[]) -> MDP:
    """
    Worst case of MDP.

    :param n: number of states
    :param a: number of actions
    :param w: weights
    :return: the MDP generated.
    """
    if not w:
        w = [1] * a
    mdp = MDP([], [], w, number_of_states=n)
    pr = [float(i) / x for i in range(1, n+1) for x in [sum(range(1, n+1))]]
    for s in range(n):
        for alpha in range(a):
            pr = pr[1:] + pr[0:1]
            to_enable = [None] * n
            for succ in range(n):
                to_enable[succ] = (succ, pr[succ])
            mdp.enable_action(s, alpha, to_enable)
    return mdp


if __name__ == '__main__':

    file_name = None
    strictly_a = '--strictly-A' in sys.argv
    complete_graph = '--complete-graph' in sys.argv
    complete_mdp = '--complete' in sys.argv or '--complete-mdp' in sys.argv
    force_weakly_connected_to = '--force-weakly-connected' in sys.argv or '--weak' in sys.argv
    weights_interval = (1, 1)
    if '--weights' in sys.argv:
        weights_interval = (int(sys.argv[sys.argv.index('--weights') + 1]),
                            int(sys.argv[sys.argv.index('--weights') + 2]))
    if '-o' in sys.argv:
        file_name = sys.argv[sys.argv.index('-o') + 1]
    number_of_states = int(sys.argv[1])
    number_of_actions = int(sys.argv[2])
    if complete_mdp:
        random_mdp = complete_MDP(number_of_states, number_of_actions, [weights_interval[1]] * number_of_actions)
    else:
        random_mdp = random_MDP(number_of_states, number_of_actions, strictly_A=strictly_a, complete_graph=complete_graph,
                                weights_interval=weights_interval,
                                force_weakly_connected_to=force_weakly_connected_to)
    yaml_parser.export_to_yaml(random_mdp, file_name)

    if not file_name:
        file_name = 'random'
    if '--viz' in sys.argv:
        graphviz.export_mdp(random_mdp, file_name)


