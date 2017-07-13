from scipy.optimize import linprog

c = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
A = [\
        [1, -4./5, 0, 0, 0, -1./5, 0, 0, 0, 0], \
        [1, -1./5, 0, 0, 0, -4./5, 0, 0, 0, 0], \
        [0, 0, -1./3, 1, -1./3, 0, -1./3, 0, 0, 0], \
        [0, 0, -9./10, 1, 0, 0, -1./10, 0, 0, 0], \
        [0, 0, 0, 1, -9./10, 0, -1./10, 0, 0, 0], \
        [0, 0, 0, 0, 0, 0, 0, -1./10, 1, -1./10], \
        [0, 0, 0, 0, 0, 0, 0, -9./10, 1, 0], \
        [0, 0, 0, 0, 0, 0, 0, 0, 1, -9./10], \
        [0, 1, 0, -1, 0, 0, 0, 0, 0, 0], \
        [-1, 0, 1, 0, 0, 0, 0, 0, 0, 0], \
        [0, 0, 0, 0, 1, 0, 0, 0, -1, 0], \
        [0, 0, 0, 0, 0, 1, 0, 0, -1, 0], \
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0], \
        [-1, 0, 0, 0, 0, 0, 0, 1, 0, 0], \
        [0, 0, 0, -1, 0, 0, 0, 0, 0, 1] \
    ]
b = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10, 4, 1, 4, 10]
res = linprog(list(map(lambda x: -1 * x, c)), A_ub=A, b_ub=b, options={"disp": True})
print(res)
