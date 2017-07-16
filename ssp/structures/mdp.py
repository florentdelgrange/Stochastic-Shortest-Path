# -*- coding: utf-8 -*-
from typing import Tuple, List, Set
from functools import reduce

class MDP:

    def __init__(self, states: List[str], actions: List[str], w: List[int]):
        self._states_name = states
        self._actions_name = actions
        self._w = w
        self._actions_enabled = [([], []) for _ in range(len(states))]
        self._pred = [set() for _ in range(len(states))]
        self._pred_alpha = [[] for _ in range(len(states))]

    def enable_action(self, s: int, alpha: int, \
                      delta_s_alpha: List[Tuple[int, float]]):
        act_s, alpha_succ = self._actions_enabled[s]
        act_s.append(alpha)
        i = len(alpha_succ)
        alpha_succ.append([])
        for (succ, pr) in delta_s_alpha:
            alpha_succ[i].append((succ, pr))
            self._pred[succ].add(s)
            self._pred_alpha[succ].add((s, alpha))

    def act(self, state: int) -> List[int]:
        return self._actions_enabled[state][0]

    def pred(self, s: int) -> Set[int]:
        return self._pred[s]

    def pred_alpha(self, s: int) -> List[int]:
        return self._pred_alpha[s]

    @property
    def number_of_states(self):
        return len(self._states_name)

    def __str__(self):
        actions_successors_for = list(map(lambda actions_successors: str((\
            list(map(lambda action: self._actions_name[action] + "|" + str(self._w[action]), actions_successors[0])),\
            list(map(lambda succ_pr_list:
                list(map(lambda succ_pr: (self._states_name[succ_pr[0]], succ_pr[1]), succ_pr_list))\
                , actions_successors[1])))),\
            self._actions_enabled))
        return reduce(lambda x, y: x + y, ([self._states_name[s] + " -> " + actions_successors_for[s] + "\n"\
            for s in range(len(self._states_name))]))[:-2]
