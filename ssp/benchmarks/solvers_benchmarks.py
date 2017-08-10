# -*- coding: utf-8 -*-
"""
Run the benchmarks :

    $ python solvers_benchmarks <options> args*

    options :
        --graphics : benchmark the sspp and sspe problem on complete MDP where the 2 last arguments are the maximum
                     number of states and maximum number of actions of these MDP . It makes growing the size of the
                     MDPs following these arguments. It generate some graphics.
                     example :
                     $ python solvers_benchmarks --graphics 10 5
        --2D : plot only 2D graphics (when --graphics is specified only).
               example :
               $ python solvers_benchmarks --graphics --2D 10 5
        --sspp: benchmark only the sspp problem on complete MDP and make growing the input length threshold of the
                problem (when --graphics is specified only).
                The arguments are:
                    arg1 : number of states of the MDP
                    arg2 : number of actions of the MDP
                    arg3 : maximum length threshold
                example :
                $ python solvers_benchmarks --graphics --sspp 10 5 100

    If you don't specify options and arguments, the program generates random MDP and benchmarks the solvers.
    Note that for the sspp problem, the length threshold is constant in this case.


"""

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
from math import log


def worst_case_benchmark(number_of_states=50, number_of_actions=10, dimensions=3) -> None:
    number_of_states += 1
    number_of_actions += 1
    T = [0]
    x = 1 if dimensions == 3 else number_of_actions - 1
    Y1 = numpy.zeros((number_of_actions, number_of_states))
    Y2 = numpy.zeros((number_of_actions, number_of_states))
    print('{:^12} | {:^15} | {:^12} | {:^19}'.format('# states (n)', '# actions (a)',
                                                     'SSPE to T', 'SSPP from s0 to T (l=5)'))
    for alpha in range(x, number_of_actions):
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
                for s in range(mdp.number_of_states):
                    force_short_paths_from(mdp, mdp.number_of_states - 1, T, 5, 0)
            time_taken = t.interval
            Y2[alpha][n] = time_taken
            print('{:^19f}'.format(time_taken))
    if dimensions == 3:
        N, A = numpy.meshgrid(range(number_of_states), range(number_of_actions))
        fig = plt.figure(figsize=(8, 6))
        ax = Axes3D(fig)
        ax.plot_surface(N, A, Y1, rstride=1, cstride=1, cmap='Blues_r')

        ax.set_xlabel("Nombre d'états")
        ax.set_ylabel("Nombre d'actions possibles par état")
        ax.set_zlabel("Temps (sec) pour résoudre le problème SSPE")
        ax.set_title("PDMP complet")

        plt.savefig('benchmarks/sspe1.png', dpi=300)
        ax.view_init(elev=30., azim=-114.)
        plt.savefig('benchmarks/sspe2.png', dpi=300)
        # plt.show()

        fig = plt.figure(figsize=(8, 6))
        ax = Axes3D(fig)
        ax.plot_surface(N, A, Y2, rstride=1, cstride=1, cmap='Reds_r')

        ax.set_xlabel("Nombre d'états")
        ax.set_ylabel("Nombre d'actions possibles par état")
        ax.set_zlabel("Temps (sec) pour résoudre le problème SSPP (l=5)")
        ax.set_title("PDMP complet")

        plt.savefig('benchmarks/sspp1.png', dpi=300)
        ax.view_init(elev=30., azim=-114.)
        plt.savefig('benchmarks/sspp2.png', dpi=300)
        # plt.show()

    if dimensions >= 2:
        fig = plt.figure(figsize=(8, 6))
        fig.suptitle('PDMP Complet avec |A| = %d' % int(number_of_actions - 1))
        fig.subplots_adjust(top=0.81)

        plt.plot(Y1[number_of_actions - 1], label="Problème de l'espérance du plus court chemin stochastique")
        plt.plot(Y2[number_of_actions - 1], label="Problème des plus courts chemins stochastiques de taille limitée "
                                                  "(l=5)")
        plt.xlabel("Nombre d'états")
        plt.ylabel("Temps (sec)")
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                   borderaxespad=0., prop={'size': 10})
        plt.savefig('benchmarks/solvers.png', dpi=300)

        fig = plt.figure(figsize=(8, 6))
        fig.suptitle('PDMP Complet avec |A| = %d (échelle logarithmique)' % int(number_of_actions - 1))
        fig.subplots_adjust(top=0.81)

        plt.plot(Y2[number_of_actions - 1], 'r',
                 label="Problème des plus courts chemins stochastiques de taille limitée "
                       "(l=5)")
        plt.xlabel("Nombre d'états")
        plt.ylabel("Temps (sec)")
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                   borderaxespad=0., prop={'size': 10})
        plt.yscale('log')
        plt.savefig('benchmarks/solvers2.png', dpi=300)


def worst_case_benchmark_sspp(number_of_states=51, number_of_actions=11, l_max=21, dimensions=3) -> None:
    number_of_states += 1
    l_max += 1
    T = [0]
    Y = numpy.zeros((l_max, number_of_states))
    x = 2 if dimensions == 3 else number_of_states - 1
    print('Number of actions : %d' % number_of_actions)
    print('{:^12} | {:^16} | {:^19}'.format('# states (n)', 'length threshold',
                                            'SSPP from s0 to T'))
    for l in range(1, l_max):
        for mdp in map(lambda s: generator.complete_MDP(s, number_of_actions),
                       range(x, number_of_states)):
            n = mdp.number_of_states
            print('{:^12d} | {:^16d} | '.format(n, l), end='')
            # expected cost to T
            t = Timer(verbose=False)
            with t:
                force_short_paths_from(mdp, mdp.number_of_states - 1, T, l, 0)
            time_taken = t.interval
            Y[l][n] = time_taken
            print('{:^19f}'.format(time_taken))

    if dimensions == 3:
        N, L = numpy.meshgrid(range(number_of_states), range(l_max))
        fig = plt.figure(figsize=(8, 6))
        ax = Axes3D(fig)
        ax.plot_surface(N, L, Y, rstride=1, cstride=1, cmap='Greens_r')

        ax.set_xlabel("Nombre d'états")
        ax.set_ylabel("l")
        ax.set_zlabel("Temps (sec) pour résoudre le problème SSPP")
        ax.set_title("PDMP complet avec |A| = %d" % number_of_actions)

        plt.savefig('benchmarks/sspp_pseudopoly1.png', dpi=300)
        ax.view_init(elev=30., azim=-114.)
        plt.savefig('benchmarks/ssp_pseudopoly15.png', dpi=300)
        # plt.show()

    fig = plt.figure(figsize=(8, 6))
    fig.suptitle('Résolution du problème SSPP pour un PDMP Complet avec |S| = %d et |A| = %d'
                 % (number_of_states - 1, number_of_actions))

    plt.plot([Y[i][number_of_states - 1] for i in range(l_max)], 'g')
    plt.xlabel("Valeur numérique de l (taille de l'entrée en unaire)")
    plt.ylabel("Temps (sec)")
    plt.savefig('benchmarks/sspp_pseudopoly2.png', dpi=300)
    # plt.show()

    fig = plt.figure(figsize=(8, 6))
    fig.suptitle('Résolution du problème SSPP pour un PDMP Complet avec |S| = %d et |A| = %d'
                 % (number_of_states - 1, number_of_actions))

    plt.plot([0.] + list(map(lambda i: log(i) / log(2) + 1, range(1, l_max))),
             [Y[i][number_of_states - 1] for i in range(0, l_max)],
             'r')

    plt.xlabel("Taille de l'entrée l en binaire")
    plt.ylabel("Temps (sec)")
    plt.savefig('benchmarks/sspp_pseudopoly3.png', dpi=300)
    # plt.show()

    fig = plt.figure(figsize=(8, 6))
    fig.suptitle('Résolution du problème SSPP pour un PDMP Complet avec |S| = %d et |A| = %d'
                 ' (échelle logarithmique)' % (number_of_states - 1, number_of_actions), fontsize=11)

    plt.plot([0.] + list(map(lambda i: log(i) / log(2) + 1, range(1, l_max))),
             [Y[i][number_of_states - 1] for i in range(0, l_max)],
             'r')
    plt.yscale('log')

    plt.xlabel("Taille de l'entrée l en binaire")
    plt.ylabel("Temps (sec)")
    plt.savefig('benchmarks/sspp_pseudopoly4.png', dpi=300)
    # plt.show()


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
    dim = 2 if "--2D" in sys.argv else 3
    if '--graphics' in sys.argv:
        if '--sspp' in sys.argv:
            n = int(sys.argv[-3])
            a = int(sys.argv[-2])
            l = int(sys.argv[-1])
            worst_case_benchmark_sspp(n, a, l, dimensions=dim)
        elif len(sys.argv) > 3:
            n = int(sys.argv[-2])
            a = int(sys.argv[-1])
            worst_case_benchmark(n, a, dimensions=dim)
        else:
            worst_case_benchmark(dimensions=dim)
    else:
        benchmark()
