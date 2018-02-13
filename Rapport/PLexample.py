for s in states:
    x[s] = pulp.LpVariable(s, lowBound=0, upBound=1)    
for s in states:
    if s in pr_max1:
        x[s] = 1
    elif not connected[s]:
        x[s] = 0
    else:
        for (alpha, successors_list) in mdp.alpha_successors(s):
            linear_program += x[s] >= sum(pr * x[succ] for (succ, pr) in successors_list)
