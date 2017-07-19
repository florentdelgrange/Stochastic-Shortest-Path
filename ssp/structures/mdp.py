# -*- coding: utf-8 -*-
from typing import Tuple, List, Set, Iterable, Iterator
from functools import reduce


class MDP:
    def __init__(self, states: List[str], actions: List[str], w: List[int],
                 number_of_states: int = -1):
        self._states_name = states
        self._actions_name = actions
        number_of_states = max(number_of_states, len(self._states_name))
        self._w = w
        self._actions_enabled: List[Tuple[List[int], List[List[Tuple[int, float]]]]] =\
            [([], []) for _ in range(number_of_states)]
        self._pred: List[Set[int]] =\
            [set() for _ in range(number_of_states)]
        self._alpha_pred: List[List[Tuple[int, int]]] =\
            [[] for _ in range(number_of_states)]

    def enable_action(self, s: int, alpha: int,
                      delta_s_alpha: Iterable[Tuple[int, float]]) -> None:
        act_s, alpha_succ = self._actions_enabled[s]
        act_s.append(alpha)
        i = len(alpha_succ)
        alpha_succ.append([])
        for (succ, pr) in delta_s_alpha:
            alpha_succ[i].append((succ, pr))
            self._pred[succ].add(s)
            self._alpha_pred[succ].append((s, len(act_s) - 1))

    def act(self, s: int) -> List[int]:
        return self._actions_enabled[s][0]

    def pred(self, s: int) -> Set[int]:
        return self._pred[s]

    def w(self, s: int) -> int:
        return self._w[s]

    def alpha_predecessors(self, s: int) -> Iterator[Tuple[int, int]]:
        return map(lambda alpha_pred: (alpha_pred[0],
                                       self.act(alpha_pred[0])[alpha_pred[1]]),
                   self._alpha_pred[s])

    def alpha_successors_iterator(self, s: int) -> Iterable[Tuple[int, int, float]]:
        return MDPIterator(self._actions_enabled[s])

    def alpha_successors(self, s: int) -> Iterator[Tuple[int, List[Tuple[int, float]]]]:
        return map(lambda alpha_i: (self._actions_enabled[s][0][alpha_i],
                                    self._actions_enabled[s][1][alpha_i]),
                   range(len(self.act(s))))

    @property
    def number_of_states(self) -> int:
        return len(self._actions_enabled)

    def state_name(self, s: int) -> str:
        if len(self._states_name) < len(self._actions_enabled):
            self._states_name = ['s' + str(i) for i in range(len(self._actions_enabled))]
        return self._states_name[s]

    def act_name(self, alpha: int) -> str:
        if len(self._actions_name) == 0:
            self._actions_name = ['a' + str(i) for i in range(len(self._w))]
        return self._actions_name[alpha]

    def __str__(self):
        self.state_name(0)
        self.act_name(0)
        actions_successors_for = list(map(lambda actions_successors: str((
            list(map(lambda action: self._actions_name[action] + "|" + str(self._w[action]), actions_successors[0])),
            list(map(lambda succ_pr_list:
                     list(map(lambda succ_pr: (self._states_name[succ_pr[0]], succ_pr[1]), succ_pr_list))
                     , actions_successors[1])))),
                                          self._actions_enabled))
        return reduce(lambda x, y: x + y, ([self._states_name[s] + " -> " + actions_successors_for[s] + "\n"
                                            for s in range(len(self._states_name))]))[:-1]


class MDPIterator:
    def __init__(self, actions_enabled: Tuple[List[int], List[List[Tuple[int, float]]]]):
        self._actions_enabled = actions_enabled
        self._current_action = 0
        self._current_tuple = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_action == len(self._actions_enabled[1]):
            raise StopIteration
        elif self._current_tuple == len(self._actions_enabled[1][self._current_action]):
            self._current_action += 1
            self._current_tuple = 0
            return self.__next__()
        alpha = self._actions_enabled[0][self._current_action]
        succ, pr = self._actions_enabled[1][self._current_action][self._current_tuple]
        self._current_tuple += 1
        return alpha, succ, pr
