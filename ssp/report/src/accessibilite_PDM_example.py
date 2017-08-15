"""
exemple 3.8
"""
from scipy.optimize import linprog

# Geometric form with min_x cx such that Ax >= b
c = [1, 1, 1]
A = [\
        [1, -4./5, -1./5],\
        [1, -1./5, -4./5],\
        [-1./3, 1, -1./3],\
        [-9./10, 1, 0],\
        [0, 1, -9./10],\
        [-1./10, -1./10, 1],\
        [-9./10, 0, 1],\
        [0, -9./10, 1]
    ]
b = [0, 0, 1./3, 1./10, 1./10, 4./5, 1./10, 1./10]
# form must be Ax <= b to be solved by the linprog algorithm
A = list(map(lambda l: list(map(lambda x: -x, l)), A))
b = list(map(lambda x: -x, b))

res = linprog(c, A_ub=A, b_ub=b, options={"disp": True})
print(res)
