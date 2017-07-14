# -*- coding: utf-8 -*-
from typing import Tuple, List, Set

class MDP:

    def __init__(self, states: List[str], actions: List[str], w: List[int]):
        self._states_name = states
        self._actions_name = actions
        self._w = w
        self._actions_enabled = [([], []) for _ in range(len(states))]
        self._succ = [set() for _ in range(len(states))]
        self._pred = [set() for _ in range(len(states))]

    def enable_action(self, s: int, alpha: int, \
                      delta_s_alpha: List[Tuple[int, float]]):
        i = len(self._actions_enabled[s])
        act_s, alpha_succ = self._actions_enabled[s]
        act_s.append(alpha)
        alpha_succ.append([])
        pr_sum = 0
        for (succ, pr) in delta_s_alpha:
            alpha_succ[i].append((succ, pr))
            self._succ[s].add(succ)
            self._pred[succ].add(s)
            pr_sum += pr

    def act(self, state: int) -> List[int]:
        return self._actions_enabled[state][0]

    def succ(self, s: int) -> Set[int]:
        return self._succ[s]

    def pred(self, s: int) -> Set[int]:
        return self._pred[s]
