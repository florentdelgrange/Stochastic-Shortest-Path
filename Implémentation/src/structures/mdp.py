# -*- coding: utf-8 -*-
from typing import Dict, Tuple, List

class MDP:

    def __init__(self, states: List[str], actions: List[str]):
        self._states_name = states
        self._actions_name = actions
        self._actions_enabled = [([], []) for i in range(len(states))]
        self._w = [0 for i in range(len(actions))]
        self._succ = [set() for i in range(len(states))]
        self._pred = [set() for i in range(len(states))]

    def enable_action(self, s: int, alpha: int, w: int, \
        delta_s_alpha: List[Tuple[int, float]]):
        self._w[alpha] = w
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
        # Check if delta is a distribution function on S.
        if(round(pr_sum, 15) != 1)
            raise RuntimeError('The transition function defined for the state '\
                + self._states_name[s] + ' and the action ' + \
                self._actions_name[alpha] + ' is not a distribution function on S.')

    def act(state: int):
        return self._actions_enabled[state][0]

    def succ(self, s: int):
        return self._succ[s]

    def pred(self, s: int):
        return self._pred[s]
