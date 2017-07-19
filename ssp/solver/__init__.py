def print_optimal_solution(x, states, state_name):
    print("Optimal solution : ")
    x_string = ['x[' + state_name(s) + ']' for s in states]
    max_length_str = max(map(len, x_string))
    max_length_int = max(map(lambda s: len(str(x[s])), states))
    print('\n'.join(('{:' + str(max_length_str) + '} = {:' + str(max_length_int) + 'g} \t' +
                     ' {:' + str(max_length_str) + '} = {:' + str(max_length_int) + 'g}').format(
        x_string[s], x[s], x_string[s + 1], x[s + 1])
                    for s in states if s + 1 < len(states) and s % 2 == 0))
    if states[-1] % 2 == 0:
        print(('{:' + str(max_length_str) + '} = {:' + str(max_length_int) + 'g} \t').format(
            x_string[states[-1]], x[states[-1]]))
