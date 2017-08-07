# -*- coding: utf-8 -*-
""" MDP module
This module contains MDP structures implementations as class.
"""
from functools import reduce
from typing import Tuple, List, Set, Iterable, Iterator

from structures.util import ReadOnlyList, Bot


class MDP:
    """ Implementation of Markov Decision Process.
    It stores actions and α-successors in a successors list following this way :
    Let s be the s th state of the MDP,

    List[ Tuple[ List[int], List[Tuple[int, int]] ]

        ┊   ┊        ┌───┐  ┌─────────────────────┬─────────────────────┬┄┄┄┄┄┄
        ┣━━━┫        │α1 │  │(s'1, ∆(s, α1, s'1)) │(s'2, ∆(s, α1, s'2)) │   ...
     s →┃  ──────→ ( ├───┤, ╞═════════════════════╪═════════════════════╪┄┄┄┄┄┄ )
        ┣━━━┫        │α2 │  │(s'k, ∆(s, α2, s'k)) ┊         ...         ┊   ...
        ┊   ┊        ├───┤  ╞═════════════════════╪─┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄
        ┊   ┊        ┊   ┊  ┊                     ┊                     ┊

    where α1, α2, ... are the enabled actions for s.
    Note that it is possible to iterate on the alpha-successors of s calling the function alpha_successors(s) that
    associates each action alpha with its alpha-successors list.

    Initialisation parameters :
        :param states: A list containing the states' names. If it is empty, the name of the s th state is
                       automatically generated when the function state_name(s) is called,
                       following the number_of_states parameter.
        :param actions: A list containing the actions' names. If it is empty, the name of the a th action is
                        automatically generated when the function action_name(a) is called, following the list of
                        actions' weight w.
        :param w: List of action's weight.
        :param number_of_states: (optional) Number of states in the MDP. Ignored if the states' name list length is
                                            greater than this parameter.
        :param validation: (optional) set this parameter to False (not recommended) if you don't want a checking on
                           values of this MDP, e.g., if you want to freely manipulate the MDP. Set this parameter to
                           False can slightly improve the performances (object initialisation speed and action enabling
                           speed can be improved), but this can provoke some errors if misused.
    """

    def __init__(self, states: List[str], actions: List[str], w: List[int],
                 number_of_states: int = -1, validation=True):
        self._states_name = states
        self._actions_name = actions
        number_of_states = max(number_of_states, len(self._states_name))
        self._w = w
        self._validation = validation
        if validation:
            if number_of_states <= 0:
                raise ValueError('The number of states must be at least 1.')
            if list(filter(lambda w_s: w_s <= 0, w)):
                raise ValueError('Weights must be > 0.')
            if not (len(w)):
                raise ValueError('The weights list is empty.')
        self._enabled_actions: List[Tuple[List[int], List[List[Tuple[int, float]]]]] = \
            [([], []) for _ in range(number_of_states)]
        self._pred: List[Set[int]] = \
            [set() for _ in range(number_of_states)]
        self._alpha_pred: List[List[Tuple[int, int]]] = \
            [[] for _ in range(number_of_states)]

    def enable_action(self, s: int, alpha: int,
                      delta_s_alpha: Iterable[Tuple[int, float]]) -> None:
        """
        Enable the action α for the state s.
        A list of α-successor linked with their probability for each α-successor is required.

        :param s: state s for which the action α will be enabled.
        :param alpha: the action to enable for the state s.
        :param delta_s_alpha: a list of tuple (succ, pr) such that
                              succ = s', pr = ∆(s, α, s') and Σ ∆(s, α, s') = 1
        """
        if self._validation:
            self._handle_value_errors(s, alpha, delta_s_alpha)
        self._enable_action(s, alpha, delta_s_alpha)

    def _handle_value_errors(self, s: int, alpha: int,
                             delta_s_alpha: Iterable[Tuple[int, float]]) -> None:
        if round(sum([pr for (_, pr) in delta_s_alpha]), 12) != 1:
            raise ValueError('The transition function formed by the ' + self.act_name(alpha) + '-successors '
                             + str(list(map(lambda succ_pr: (self.state_name(succ_pr[0]), succ_pr[1]),
                                            delta_s_alpha))) + ' for the state '
                             + self.state_name(s) + ' and the action '
                             + self.act_name(alpha) + ' is not a distribution function on the states of this MDP.')
        if list(filter(lambda succ_pr: not (0 < succ_pr[1] <= 1), delta_s_alpha)):
            raise ValueError('These following ' + self.act_name(alpha) + '-successors of %s: ' % self.state_name(s) +
                             str(list(filter(lambda succ_pr: not (0 < succ_pr[1] <= 1), delta_s_alpha))) +
                             " do not respect 0 < ∆(%s, %s, %s) <= 1."
                             % (self.state_name(s), self.act_name(alpha), "s'"))

    def _enable_action(self, s: int, alpha: int,
                       delta_s_alpha: Iterable[Tuple[int, float]]) -> None:
        act_s, alpha_succ = self._enabled_actions[s]
        act_s.append(alpha)
        i = len(alpha_succ)
        alpha_succ.append([])
        for (succ, pr) in delta_s_alpha:
            alpha_succ[i].append((succ, pr))
            self._pred[succ].add(s)
            self._alpha_pred[succ].append((s, len(act_s) - 1))

    def disable_action(self, s: int, alpha: int) -> None:
        """
        Disable the action alpha for the state s

        :param s: a state of this MDP.
        :param alpha: an action enabled for s.
        """
        i = self.act(s).index(alpha)
        del self._enabled_actions[s][0][i]
        del self._enabled_actions[s][1][i]

    def act(self, s: int) -> List[int]:
        """
        Get the list of actions enabled for s, i.e., A(s).

        :param s: a state of this MDP.
        :return: the actions enabled for this state s.
        """
        return ReadOnlyList(self._enabled_actions[s][0])

    def pred(self, s: int) -> Set[int]:
        """
        Get the set of predecessors of s in the underlying graph of this MDP.

        :param s: a state of this MDP.
        :return: the predecessors of s in the underlying graph of this MDP.
        """
        return self._pred[s]

    def w(self, alpha: int) -> int:
        """
        Get the weight of an action α, i.e., w(α).

        :param alpha: an action of this MPD.
        :return: the weight of the action α, i.e., w(α).
        """
        return self._w[alpha]

    def alpha_predecessors(self, s: int) -> Iterator[Tuple[int, int]]:
        """
        Get an iterator on the set Pred(s) = { (s*, α) | ∆(s*, α, s) > 0 }

        :param s: a state of this MDP.
        :return: an iterator on Pred(s).
        """
        return map(lambda alpha_pred: (alpha_pred[0],
                                       self.act(alpha_pred[0])[alpha_pred[1]]),
                   self._alpha_pred[s])

    def alpha_successors(self, s: int) -> Iterator[Tuple[int, List[Tuple[int, float]]]]:
        """
        Get an iterator on the α-successors of s.
        Indeed, let α ∈ A(s) be the first action enabled of s, i.e., act(s)[0].
        Then, next(alpha_successors(s)) = (α, α-succ) where α-succ a list of the α-successors of s, i.e.
        an list of element of the set SuccPr(s, α) = { (s', pr) | ∆(s, α, s') > 0 and pr = ∆(s, α, s') }

        :param s: a state of this MDP.
        :return: an iterator as described above.
        """
        return map(lambda alpha_i: (self._enabled_actions[s][0][alpha_i],
                                    ReadOnlyList(self._enabled_actions[s][1][alpha_i])),
                   range(len(self.act(s))))

    @property
    def number_of_states(self) -> int:
        """
        Get the number of states of this MPD.

        :return: the number of states of this MDP.
        """
        return len(self._enabled_actions)

    @property
    def number_of_actions(self) -> int:
        """
        Get the number of actions of this MDP.

        :return: the number of actions of this MDP.
        """
        return len(self._w)

    def state_index(self, name: str):
        """
        Get the index of the state labeled with the name in parameter.

        :param name: the label of a state.
        :return: the index of this state.
        """
        try:
            return self._states_name.index(name)
        except:
            raise ValueError('No state labeled %s in this MDP.' % name)

    def action_index(self, name: str):
        """
        Get the index of the action labeled with the name in parameter.

        :param name: label of an action.
        :return: the index of this action.
        """
        try:
            return self._actions_name.index(name)
        except:
            raise ValueError('No action labeled %s in this MDP.' % name)

    def state_name(self, s: int) -> str:
        """
        Get the name of the state s.

        :param s: a state of this MDP.
        :return: the name of the state s.
        """
        # First, generate names if an issue is detected on self._state_name, the list of state_name initialized
        # at the same time as the MDP.
        self._generate_names()
        try:
            return self._states_name[s]
        except:
            raise IndexError('A state with index %d does not exist in this MDP.' % s)

    def act_name(self, alpha: int) -> str:
        """
        Get the name of the action α.

        :param alpha: an action of this MDP.
        :return: the name of the action alpha.
        """
        self._generate_names()
        try:
            return self._actions_name[alpha]
        except:
            raise IndexError('An action with index %d does not exist in this MDP.' % alpha)

    def _generate_names(self):
        if len(self._states_name) < len(self._enabled_actions):
            self._states_name = ['s' + str(i) for i in range(len(self._enabled_actions))]
        if len(self._actions_name) != len(self._w):
            self._actions_name = ['a' + str(i) for i in range(len(self._w))]

    def __str__(self):
        actions_successors_for = list(map(lambda actions_successors: str((
            list(map(lambda action: self.act_name(action) + "|" + str(self._w[action]), actions_successors[0])),
            list(map(lambda succ_pr_list:
                     list(map(lambda succ_pr: (self.state_name(succ_pr[0]), succ_pr[1]), succ_pr_list))
                     , actions_successors[1])))),
                                          self._enabled_actions))
        return reduce(lambda x, y: x + y, ([self.state_name(s) + " -> " + actions_successors_for[s] + "\n"
                                            for s in range(self.number_of_states)]))[:-1]


class UnfoldedMDP(MDP):
    """ Unfold an MDP following an initial state (s0), a list of target states (T) and a maximum length threshold (l)
    (@see stochastic shortest path percentile problem in solvers.sspp).
    The states of this new MDP take the following form : (s, v) where s is a state of the initial MDP and v is the
    current traveled length.
    This generates a new MDP object from a MDP and these parameters on which the reachability to
    T* = { (t, v) | t ∈ T and v <= l } can be computed.

    Initialisation parameters :
        :param mdp: the initial MDP to unfold.
        :param s0: the initial state from which the mdp will be unfolded.
        :param T: target states.
        :param l: maximum length threshold.
        :param v: (optional) set this parameter if you want an initial state (s0, v) where v > 0.
    """

    def __init__(self, mdp: MDP, s0: int, T: List[int], l: int, v: int = 0, validation=True):
        mdp._generate_names()
        self._states_name = mdp._states_name + ['⊥']
        self._actions_name = mdp._actions_name + ['loop']
        self._validation = False
        self._w = mdp._w + [1]
        self._enabled_actions: List[Tuple[List[int], List[List[Tuple[int, float]]]]] = []
        self._pred: List[Set[int]] = []
        self._alpha_pred: List[List[Tuple[int, int]]] = []
        self._T = []

        bot_alpha_pred = []
        Tset = set(T)
        # dict version
        A = [{} for _ in range(mdp.number_of_states)]
        # matrix version
        # A = [[None] * (l + 1) for _ in range(mdp.number_of_states)]
        # self._convert is used to convert a state index in this MDP to the real (s, v) where s is a state in the
        # initial MDP.
        self._convert = []
        self._number_of_states = 0

        def fill(s: int):
            if s == len(self._enabled_actions):
                self._enabled_actions.append(([], []))
                self._pred.append(set())
                self._alpha_pred.append([])

        def unfold(s, v):
            """
            Build recursively the unfolded MDP from the initial MDP.

            :param s: current state.
            :param v: current path length.
            :return: the index of (s, v) in this unfolded MDP.
            """
            # get the index of (s, v) in the unfolded MDP. If (s, v) has no index, a new index is allocated to it.
            # dict version
            i = A[s][v] = A[s].get(v, self._number_of_states)
            # matrix version
            # i = A[s][v] if A[s][v] else self._number_of_states
            # A[s][v] = i
            # if a new index is allocated to s, it is because s was never considered. So an unfolding from s
            # is required. The following code enable the actions α of (s, v) and compute its α-successors.
            if i == self._number_of_states:
                self._convert.append((s, v))
                self._number_of_states += 1
                fill(i)
                if s in Tset:
                    # it is unless to continue the unfold from t if s ∈ T because it will not be considered by the
                    # reachability problem solver. So, only the action 'loop' is enabled for s and ∆(s, 'loop', s) = 1.
                    self.enable_action(i, len(self._w) - 1, [(i, 1)])
                    self._T.append(i)
                else:
                    for (alpha, succ_list) in mdp.alpha_successors(s):
                        if v + mdp.w(alpha) > l:
                            bot_alpha_pred.append((i, alpha))
                        else:
                            v_new = v + mdp.w(alpha)
                            to_enable = []
                            for (succ, pr) in succ_list:
                                j = unfold(succ, v_new)
                                to_enable.append((j, pr))
                            self.enable_action(i, alpha, to_enable)
            return i

        import sys
        sys.setrecursionlimit(3000)
        unfold(s0, v)
        # Add the ⊥ state. It corresponds to all states (s, v) such that v > l. Its only enabled action is 'loop'.
        self._convert.append((-1, Bot()))
        self._enabled_actions.append(([len(self._w) - 1], [[(len(self._enabled_actions), 1)]]))
        self._pred.append(set())
        self._alpha_pred.append([])
        for (pred, alpha) in bot_alpha_pred:
            self.enable_action(pred, alpha, [(self._number_of_states, 1)])
        self._validation = validation

    @property
    def target_states(self):
        """
        Get the list of the target states in T = { (t, v) | t ∈ T_old and v <= l } such that T_old is the set of target
        states in the initial MDP.

        :return: the list of index of states from the set T described above.
        """
        return self._T

    def state_name(self, s: int) -> str:
        s, v = self._convert[s]
        if s != -1:
            return '(' + self._states_name[s] + ', ' + str(v) + ')'
        else:
            return '⊥'

    def state_index(self, name: str):
        """
        Get the index of the state labeled with the name in parameter.
        Format : '(state_name, v)'

        :param name: the label of a state.
        :return: the index of this state.
        """
        name_list = list(name)
        name_list.remove('(')
        name_list.reverse()
        name_list.remove(')')
        first = False
        s = ''
        v = ''
        for char in name_list:
            if first:
                s = char + s
            elif char != ',':
                if char != " ":
                    v = char + v
            else:
                v = int(v)
                first = True

        try:
            i = self._states_name.index(s)
            for state in range(self.number_of_states):
                if self._convert[state] == (i, v):
                    return state
        except:
            raise ValueError('No state labeled %s in the MDP.' % s)
        raise ValueError('No state labeled (%s, %d) in this unfolded MDP.' % (s, v))

    def _generate_names(self):
        pass

    def convert(self, s: int) -> Tuple[int, int]:
        """
        Convert the state index s in this MDP to (s*, v), where s* is a state from the initial MDP and v is the current
        path length value.

        :param s: s th state in this unfolded MDP.
        :return: (s*, v) where s* is a state from the initial MDP and v is the current path length.
        """
        return self._convert[s]


class SelfGrowingMDP(MDP):
    def __init__(self, max_size: int):
        super().__init__([], [], [1, 1], number_of_states=2)
        self._max_size = max_size
        self.enable_action(0, 0, [(0, 1)])
        self.enable_action(1, 0, [(0, 1. / 2), (1, 1. / 2)])
        self.enable_action(1, 1, [(0, 1)])

        self._iter = False
        self._absorbing_states = {0}
        self._last_absorbing_state = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.number_of_states >= self._max_size:
            raise StopIteration
        if not self._iter:
            self._iter = True
            return self
        else:
            # self._validation = False

            current_s = self.number_of_states
            self._enabled_actions.append(([], []))
            self._pred.append(set())
            self._alpha_pred.append([])

            pr = 1. / (self.number_of_states - len(self._absorbing_states))

            if float(self.number_of_states) >= 1. / 20 * self._max_size * (len(self._absorbing_states))\
                    and current_s - 1 != self._last_absorbing_state:
                self._last_absorbing_state = current_s
                print(self._last_absorbing_state)
                self.enable_action(current_s, 0, [(current_s, 1)])
            else:
                for alpha in range(self.number_of_actions):
                    to_enable = []
                    current_pr = 0.
                    for s in range(self.number_of_states):
                        if s not in self._absorbing_states:
                            if s == current_s:
                                to_enable.append((s, 1 - current_pr))
                            else:
                                current_pr += pr / (alpha + 1)
                                to_enable.append((s, (pr / (alpha + 1))))
                    self.enable_action(current_s, alpha, to_enable)
                if self._last_absorbing_state == current_s - 1:
                    self._absorbing_states.add(self._last_absorbing_state)
                    self._absorbing_states.add(current_s)
            if float(self.number_of_actions) < float(self.number_of_states) / 5:
                print('>>> NEW ACTION ADDED <<<')
                self._w.append(1)
                for s in range(1, self.number_of_states):
                    if s not in self._absorbing_states:
                        self.enable_action(s, self.number_of_actions - 1,
                                           [(s, pr) for s in range(self.number_of_states) if
                                            s not in self._absorbing_states])

            # self._validation = True
            return self
