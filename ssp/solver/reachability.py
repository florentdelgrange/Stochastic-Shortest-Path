from structures.mdp import MDP
from typing import List

def reach(mdp: MDP, T: List[int]):
    x = [-1 for _ in range(mdp.number_of_states)]
    for t in T:
        x[t] = 1
    connected_to_T = connected_to(mdp, T)
    for s in filter(lambda s: not connected_to_T[s],\
    range(mdp.number_of_states)):
        x[s] = 0

def connected_to(mdp: MDP, T: List[int]) -> List[bool]:
    marked = [False for _ in range(mdp.number_of_states)]
    for t in T:
        marked[t] = True
    next = []
    for t in T:
        next.extend(mdp.pred(t))
    predecessors = []
    while(next):
        predecessors = next
        next = []
        for pred in predecessors:
            if not marked[pred]:
                marked[pred] = True
                next.extend(mdp.pred(pred))
    return marked

def minimal_steps_number_to(mdp: MDP, T: List[int]) -> List[int]:
    steps = [float('inf') for _ in range(mdp.number_of_states)]
    for t in T:
        steps[t] = 0
    next = []
    for t in T:
        next.extend(mdp.pred(t))
    i = 1
    predecessors = []
    while(next):
        predecessors = next
        next = []
        for pred in predecessors:
            if steps[pred] > i:
                steps[pred] = i
                next.extend(mdp.pred(pred))
        i += 1
    return steps

def pr_max_1(MDP: mdp, T: List[int], x: List[float]) -> List[int]:
    u = list(filter(lambda x: x[s] != 0, range(len(x))))
    while(u):
        r = u
        
