import pulp

from solver import print_optimal_solution
from structures.mdp import MDP
from typing import List, Callable
from collections import deque

act_max = []


def reach(mdp: MDP, T: List[int], msg=0, solver: pulp=pulp.GLPK_CMD()) -> List[float]:
    states = list(range(mdp.number_of_states))
    # x[s] is the Pr^max to reach T
    x = [-1 for _ in states]
    connected = connected_to(mdp, T)

    # find all states s such that s is not connected to T
    for s in filter(lambda s: not connected[s], states):
        x[s] = 0
    # act_max contains the list of actions, for all s, that maximize the Pr to reach T
    global act_max
    act_max = [[] for _ in states]
    # find all states s such that Pr^max to reach T is 1
    for s in pr_max_1(mdp, T, connected=connected, act_max=act_max):
        x[s] = 1

    # if there exist some states such that Pr^max to reach T is is ]0, 1[
    if list(filter(lambda s: x[s] != 1 and x[s] != 0, states)):

        # formulate the LP problem
        linear_program = pulp.LpProblem("reachability", pulp.LpMinimize)
        # initialize variables
        for s in filter(lambda s: x[s] == -1, states):
            x[s] = pulp.LpVariable(mdp.state_name(s), lowBound=0)
        # objective function
        linear_program += sum(x)
        # constraints
        for s in filter(lambda s: x[s] != 0 and x[s] != 1, states):
            for (alpha, successor_list) in mdp.alpha_successors(s):
                linear_program += x[s] >= sum(map(lambda succ_pr: succ_pr[1] * x[succ_pr[0]], successor_list))
        if msg:
            print(linear_program)

        # solve the LP
        solver.msg = msg
        linear_program.solve(solver)

        for s in states:
            if x[s] != 0 and x[s] != 1:
                x[s] = x[s].varValue

    if msg:
        print_optimal_solution(x, states, mdp.state_name)

    return x


def scheduler(mdp: MDP, T: List[int], solver: pulp=pulp.GLPK_CMD()) -> Callable[[int], int]:
    x = reach(mdp, T, solver=solver)

    states = range(mdp.number_of_states)

    # update act_max
    for s in filter(lambda s: not act_max[s], states):
        pr_max = 0
        for (alpha, successor_list) in mdp.alpha_successors(s):
            pr = sum(map(lambda succ_pr: succ_pr[1] * x[succ_pr[0]], successor_list))
            if pr == pr_max:
                act_max[s].append(alpha)
            elif pr > pr_max:
                pr_max = pr
                act_max[s] = [alpha]

    # compute M^max
    mdp_max = MDP([], [], [], mdp.number_of_states)
    for s in states:
        i = 0
        for (alpha, successor_list) in mdp.alpha_successors(s):
            if alpha == act_max[s][i]:
                i += 1
                mdp_max.enable_action(s, alpha, successor_list)
            if i == len(act_max[s]):
                break

    # compute the final scheduler
    minimal_steps = minimal_steps_number_to(mdp_max, T)
    scheduler: List[int] = []
    for s in states:
        if x[s] == 0 or minimal_steps[s] == 0:
            scheduler.append(act_max[s][0])
        else:
            for (alpha, successor_list) in mdp_max.alpha_successors(s):
                for (succ, pr) in successor_list:
                    if minimal_steps[succ] == minimal_steps[s] - 1:
                        scheduler.append(alpha)
                        break
                if len(scheduler) == s - 1:
                    break

    return lambda s: scheduler[s]


def connected_to(mdp: MDP, T: List[int]) -> List[bool]:
    marked = [False for _ in range(mdp.number_of_states)]
    for t in T:
        marked[t] = True
    next = []
    for t in T:
        next.extend(mdp.pred(t))
    while next:
        predecessors = next
        next = []
        for pred in predecessors:
            if not marked[pred]:
                marked[pred] = True
                next.extend(mdp.pred(pred))
    return marked


def minimal_steps_number_to(mdp: MDP, T: List[int]) -> List[float]:
    steps = [float('inf') for _ in range(mdp.number_of_states)]
    for t in T:
        steps[t] = 0
    next = []
    for t in T:
        next.extend(mdp.pred(t))
    i = 1
    while next:
        predecessors = next
        next = []
        for pred in predecessors:
            if steps[pred] > i:
                steps[pred] = i
                next.extend(mdp.pred(pred))
        i += 1
    return steps


def pr_max_1(mdp: MDP, T: List[int], act_max: List[List[int]]=[], connected: List[bool]=[]) -> List[int]:
    if not connected:
        connected = connected_to(mdp, T)
    removed_state = [False for _ in range(mdp.number_of_states)]
    in_T = [False for _ in range(mdp.number_of_states)]
    for t in T:
        in_T[t] = True
    disabled_action = [[False for _ in range(len(mdp.act(s)))]
                       for s in range(mdp.number_of_states)]
    no_disabled_actions = [0 for _ in range(mdp.number_of_states)]

    U = [s for s in range(mdp.number_of_states) if not connected[s]]
    while len(U) > 0:
        R = deque(U)
        while len(R) > 0:
            u = R.pop()
            for (t, alpha_i) in mdp._alpha_pred[u]:
                if connected[t] and not disabled_action[t][alpha_i] and not in_T[t]:
                    disabled_action[t][alpha_i] = True
                    no_disabled_actions[t] += 1
                    if no_disabled_actions[t] == len(mdp.act(t)):
                        R.appendleft(t)
                        connected[t] = False
            removed_state[u] = True
        sub_mdp = MDP([], [], [], number_of_states=mdp.number_of_states)
        for s in range(mdp.number_of_states):
            if not removed_state[s]:
                for alpha_i in range(len(mdp.act(s))):
                    if not disabled_action[s][alpha_i]:
                        sub_mdp.enable_action(s, mdp._actions_enabled[s][0][alpha_i],
                                              filter(lambda succ_pr: not removed_state[succ_pr[0]],
                                                     mdp._actions_enabled[s][1][alpha_i]))
        mdp = sub_mdp
        connected = connected_to(mdp, T)
        connected = [connected[s] and not removed_state[s] for s in range(mdp.number_of_states)]
        U = [s for s in range(mdp.number_of_states)
             if not connected[s] and not removed_state[s]]
    pr_1 = [s for s in range(mdp.number_of_states) if not removed_state[s]]
    if act_max:
        for s in pr_1:
            act_max[s] = mdp.act(s)
    return pr_1
