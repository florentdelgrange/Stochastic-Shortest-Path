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


def build_and_benchmark(number_of_states=51, number_of_actions=10) -> None:
    T = [0]
    x = list(range(2, number_of_states))
    y1 = []
    y2 = []
    Y1 = numpy.zeros((number_of_actions, number_of_states))
    Y2 = numpy.zeros((number_of_actions, number_of_states))
    print('{:^12} | {:^15} | {:^12} | {:^19}'.format('# states (n)', '# actions (a)',
                                                     'SSPE to T', 'SSPP from s0 to T (l=5)'))
    for alpha in range(1, number_of_actions):
        for mdp in map(lambda s: generator.worst_case_MDP(s, alpha), range(2, number_of_states)):
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

    ax.set_xlabel("Nombre de sommets", fontsize=8)
    ax.set_ylabel("Nombre d'actions possibles par sommet", fontsize=8)
    ax.set_zlabel("Temps (sec) pour résoudre le problème SSPE", fontsize=8)
    ax.set_title("PDMP complet")

    plt.savefig('benchmarks/sspe.png')
    plt.show()

    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot_surface(N, A, Y2, rstride=1, cstride=1, cmap='Reds_r')

    ax.set_xlabel("Nombre de sommets", fontsize=8)
    ax.set_ylabel("Nombre d'actions possibles par sommet", fontsize=7)
    ax.set_zlabel("Temps (sec) pour résoudre le problème SSPP (l=5)", fontsize=7)
    ax.set_title("PDMP complet")

    plt.savefig('benchmarks/sspp.png')
    plt.show()
    print(65 * '-')
    for mdp in map(lambda s: generator.worst_case_MDP(s, 5), range(2, number_of_states)):
        n = mdp.number_of_states
        number_of_actions = mdp.number_of_states ** 2 * mdp.number_of_actions
        print('{:^12d} | {:^15d} | '.format(n, number_of_actions), end='')
        # expected cost to T
        t = Timer(verbose=False)
        with t:
            min_expected_cost(mdp, T)
        time_taken = t.interval
        y1.append(time_taken)
        print('{:^12f} | '.format(time_taken), end='')

        # SSPP
        t = Timer(verbose=False)
        with t:
            force_short_paths_from(mdp, mdp.number_of_states - 1, T, 5, 0)
        time_taken = t.interval
        y2.append(time_taken)
        print('{:^19f}'.format(time_taken))

    fig = plt.figure()
    fig.suptitle('PDMP Complet avec |A| = 5', fontsize=14)
    fig.subplots_adjust(top=0.81)

    plt.plot(y1, label="Problème de l'espérance du plus court chemin stochastique")
    plt.plot(y2, label="Problème des plus courts chemins stochastiques de taille limitée (l=5)")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
               borderaxespad=0.)
    plt.savefig('benchmarks/solvers.png')
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
    if '--graphics' in sys.argv:
        build_and_benchmark()
    else:
        benchmark()
