# -*- coding: utf-8 -*-

import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from solvers.sspe import min_expected_cost
from solvers.sspp import force_short_paths_from
from structures import generator
from solvers.reachability import reach
import timeit
from benchmarks.timer import Timer


def timeit_benchmark():
    for (n, a) in [(1000, 2), (1000, 5), (2000, 2), (2000, 5), (2000, 10), (5000, 20)]:
        print('Random_mdp(n=%d,a=%d)' % (n, a))
        print('1. Reachability to s1')
        print(timeit.timeit("reach(mdp , [1], msg=0)", setup="from solvers.reachability import reach; from structures "
                                                             "import "
                                                             "generator; mdp = generator.random_MDP(%d, %d)" % (n, a),
                            number=1))
        print('2. Stochastic Shortest Path Expectation to s1')
        print(timeit.timeit("min_expected_cost(mdp , [1])", setup="from solvers.sspe import min_expected_cost; "
                                                                  "from structures "
                                                                  "import generator; mdp = "
                                                                  "generator.random_MDP(%d, %d, %s)" % (
                                                                      n, a, 'weights_interval=[1, 10]'),
                            number=1))
        print('3. Stochastic Shortest Path Percentile from s0 to s1 with a path < number of states')
        print(
            timeit.timeit("force_short_paths_from(mdp, 0, [1], %d)" % n, setup="from solvers.sspp import "
                                                                               "force_short_paths_from; "
                                                                               "from structures "
                                                                               "import generator; mdp = "
                                                                               "generator.random_MDP(%d, %d)" % (
                                                                                   n, a),
                          number=1))


if __name__ == '__main__':
    print('{:^30} | {:^12} | {:^15} | {:^13} | {:^17} | {:^9} | {:^9}'.format('Random MDP properties',
                                                                              '# states (n)', '# actions (a)',
                                                                              'time to build', 'reachability to T',
                                                                              'SSPE to T', 'SSPP from s0 to T (l=5)'))
    print(135 * '-')
    T = [1]
    for x in [100, 200, 500, 1000, 1500, 2000]:
        for y in [5, 10, 20, 50]:
            for (name, n, a, strictly_a, complete, force_weakly_connected_to_T) in [
                ('Any', x, y, False, False, False),
                ('Complete', x, y, False, True, False),
                ('Weakly connected to T', x, y, False, False, True),
                ('|A(s)| = a ∀s', x, y, True, False, False),
                ('Complete & |A(s)| = a ∀s', x, y, True, True, False)
            ]:
                print('{:^30} | {:^12d} | {:^15d} | '.format(name, n, a), end='')

                # Building a random MDP
                t = Timer(verbose=False)
                with t:
                    mdp = generator.random_MDP(n, a, strictly_a=strictly_a, complete_graph=complete,
                                               force_weakly_connected_to=force_weakly_connected_to_T)
                time_taken = t.interval
                print('{:^13f} | '.format(time_taken), end='')

                # reach T
                t = Timer(verbose=False)
                with t:
                    reach(mdp, T)
                time_taken = t.interval
                print('{:^17f} | '.format(time_taken), end='')

                # expected cost to T
                t = Timer(verbose=False)
                with t:
                    min_expected_cost(mdp, T)
                time_taken = t.interval
                print('{:^9f} | '.format(time_taken), end='')

                # SSPP
                t = Timer(verbose=False)
                with t:
                    force_short_paths_from(mdp, 0, T, 5)
                time_taken = t.interval
                print('{:^19f}'.format(time_taken))
