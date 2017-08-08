# -*- coding: utf-8 -*-

import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from solvers.sspe import min_expected_cost
from solvers.sspp import force_short_paths_from
from structures import generator
from solvers.reachability import reach
from benchmarks.timer import Timer
import matplotlib.pyplot as plt
import numpy
from mpl_toolkits.mplot3d import Axes3D


def worst_case_polynomial_benchmark(number_of_states=51, number_of_actions=11) -> None:
    T = [0]
    Y1 = numpy.zeros((number_of_actions, number_of_states))
    Y2 = numpy.zeros((number_of_actions, number_of_states))
    print('{:^12} | {:^15} | {:^12} | {:^19}'.format('# states (n)', '# actions (a)',
                                                     'SSPE to T', 'SSPP from s0 to T (l=5)'))
    for alpha in range(1, number_of_actions):
        for mdp in map(lambda s: generator.complete_MDP(s, alpha), range(2, number_of_states)):
            n = mdp.number_of_states
            print('{:^12d} | {:^15d} | '.format(n, alpha), end='')
            # expected cost to T
            t = Timer(verbose=False)
            with t:
                min_expected_cost(mdp, T)
            time_taken = t.interval
            Y1[alpha][n] = time_taken
            print('{:^12f} | '.format(time_taken), end='')
            # SSPP
            t = Timer(verbose=False)
            with t:
                force_short_paths_from(mdp, mdp.number_of_states - 1, T, 5, 0)
            time_taken = t.interval
            Y2[alpha][n] = time_taken
            print('{:^19f}'.format(time_taken))

    N, A = numpy.meshgrid(range(number_of_states), range(number_of_actions))
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot_surface(N, A, Y1, rstride=1, cstride=1, cmap='Blues_r')

    ax.set_xlabel("Nombre d'états", fontsize=14)
    ax.set_ylabel("Nombre d'actions possibles par état", fontsize=14)
    ax.set_zlabel("Temps (sec) pour résoudre le problème SSPE", fontsize=14)
    ax.set_title("PDMP complet")

    plt.savefig('benchmarks/sspe.png')
    plt.show()

    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot_surface(N, A, Y2, rstride=1, cstride=1, cmap='Reds_r')

    ax.set_xlabel("Nombre d'états", fontsize=14)
    ax.set_ylabel("Nombre d'actions possibles par état", fontsize=14)
    ax.set_zlabel("Temps (sec) pour résoudre le problème SSPP (l=5)", fontsize=14)
    ax.set_title("PDMP complet")

    plt.savefig('benchmarks/sspp.png')
    plt.show()

    fig = plt.figure()
    fig.suptitle('PDMP Complet avec |A| = %d' % int(number_of_actions - 1))
    fig.subplots_adjust(top=0.81)

    plt.plot(Y1[number_of_actions - 1], label="Problème de l'espérance du plus court chemin stochastique")
    plt.plot(Y2[number_of_actions - 1], label="Problème des plus courts chemins stochastiques de taille limitée "
                                              "(l=5)")
    plt.xlabel("Nombre d'états", fontsize=14)
    plt.ylabel("Temps (sec)", fontsize=14)
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
               borderaxespad=0., prop={'size': 14})
    plt.savefig('benchmarks/solvers.png')
    plt.show()


def worst_case_pseudo_polynomial_benchmark(number_of_states=51, number_of_actions=11, l_max=31) -> None:
    T = [0]
    Y = numpy.zeros((l_max, number_of_states))
    print('Number of actions : %d' % number_of_actions)
    print('{:^12} | {:^16} | {:^19}'.format('# states (n)', 'length threshold',
                                            'SSPP from s0 to T'))
    for l in range(1, l_max):
        for mdp in map(lambda s: generator.complete_MDP(s, number_of_actions), range(2, number_of_states)):
            n = mdp.number_of_states
            print('{:^12d} | {:^16d} | '.format(n, l), end='')
            # expected cost to T
            t = Timer(verbose=False)
            with t:
                force_short_paths_from(mdp, mdp.number_of_states - 1, T, l, 0)
            time_taken = t.interval
            Y[l][n] = time_taken
            print('{:^19f}'.format(time_taken))

    N, L = numpy.meshgrid(range(number_of_states), range(l_max))
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot_surface(N, L, Y, rstride=1, cstride=1, cmap='Greens_r')

    ax.set_xlabel("Nombre d'états", fontsize=14)
    ax.set_ylabel("l", fontsize=14)
    ax.set_zlabel("Temps (sec) pour résoudre le problème SSPP", fontsize=14)
    ax.set_title("PDMP complet avec |A| = %d" % number_of_actions)

    plt.savefig('benchmarks/sspp_pseudopoly.png')
    plt.show()

    fig = plt.figure()
    fig.suptitle('PDMP Complet avec |S| = %d et |A| = %d' % (number_of_states - 1, number_of_actions))
    fig.subplots_adjust(top=0.81)

    plt.plot([Y[i][number_of_states - 1] for i in range(l_max)], 'g',
             label="Problème des plus courts chemins stochastiques de taille limitée par l")

    plt.xlabel("l", fontsize=14)
    plt.ylabel("Temps (sec)", fontsize=14)
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
               borderaxespad=0., prop={'size': 14})
    plt.savefig('benchmarks/sspp_pseudopoly2.png')
    plt.show()


def benchmark() -> None:
    print('{:^30} | {:^12} | {:^15} | {:^16} | {:^17} | {:^12} | {:^19}'.format('Random MDP properties',
                                                                                '# states (n)', '# actions (a)',
                                                                                'time to generate', 'reachability to T',
                                                                                'SSPE to T', 'SSPP from s0 to T (l=5)'))
    print(143 * '-')
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
                    mdp = generator.random_MDP(n, a, strictly_A=strictly_a, complete_graph=complete,
                                               force_weakly_connected_to=force_weakly_connected_to_T)
                time_taken = t.interval
                print('{:^16f} | '.format(time_taken), end='')

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
                print('{:^12f} | '.format(time_taken), end='')

                # SSPP
                t = Timer(verbose=False)
                with t:
                    force_short_paths_from(mdp, 0, T, 5, 0)
                time_taken = t.interval
                print('{:^19f}'.format(time_taken))


if __name__ == '__main__':
    if '--polynomial' in sys.argv:
        if len(sys.argv) > 2:
            n = int(sys.argv[2])
            a = int(sys.argv[3])
            worst_case_polynomial_benchmark(n, a)
        else:
            worst_case_polynomial_benchmark()
    if '--pseudo-polynomial' in sys.argv:
        if len(sys.argv) > 2:
            n = int(sys.argv[2])
            a = int(sys.argv[3])
            worst_case_pseudo_polynomial_benchmark(n, a)
        else:
            worst_case_pseudo_polynomial_benchmark()
    else:
        benchmark()
