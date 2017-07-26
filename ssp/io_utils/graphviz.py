from graphviz import Digraph
from structures.mdp import MDP


def export_mdp(mdp: MDP, mdp_name: str) -> None:
    states = range(mdp.number_of_states)

    g = Digraph(mdp_name, filename=mdp_name + '.gv')

    g.attr('node', shape='circle')
    for s in states:
        g.node('s%d' % s, label=mdp.state_name(s))

    g.attr('node', shape='point')
    for s in states:
        for (alpha, succ_list) in mdp.alpha_successors(s):
            g.node('s%d->a%d' % (s, alpha),
                   xlabel=' ' + mdp.act_name(alpha) + ' | ' + str(mdp.w(alpha)) + ' ', fontsize='8')
            g.edge('s%d' % s, 's%d->a%d' % (s, alpha))
            for (succ, pr) in succ_list:
                g.edge('s%d->a%d' % (s, alpha), 's%d' % succ, label=str(round(pr, 4)), fontsize='8')

    g.view()
