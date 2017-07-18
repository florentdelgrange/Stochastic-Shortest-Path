from functools import reduce
import yaml
from structures.mdp import MDP


def import_from_yaml(stream) -> MDP:
    mdp_dict = yaml.load(stream)['mdp']
    mdp_states = mdp_dict['states']
    mdp_actions = mdp_dict['actions']
    states = [state['name'] for state in mdp_states]
    state_from_name = {}
    for i in range(len(mdp_states)):
        state_from_name[states[i]] = i
    actions = [action['name'] for action in mdp_actions]
    w = [int(action['weight']) for action in mdp_actions]
    if list(filter(lambda weight: weight <= 0, w)):
        raise RuntimeError('A weight is inferior than 0')
    action_from_name = {}
    for i in range(len(mdp_actions)):
        action_from_name[actions[i]] = i

    mdp = MDP(states, actions, w)
    for s in range(len(states)):
        enabled_actions = mdp_states[s]['enabled actions']
        for enabled_action in enabled_actions:
            transitions = [(state_from_name[transition['target']], \
                            str_to_float(str(transition['probability']))) \
                           for transition in enabled_action['transitions']]

            alpha = enabled_action['name']

            # Check if delta is a distribution function on S.
            if round(sum([pr for (_, pr) in transitions]), 15) != 1:
                raise RuntimeError('The transition function defined for the state ' \
                                   + states[s] + ' and the action ' + \
                                   alpha + ' is not a distribution function on S.')

            # enable this action in the MDP
            mdp.enable_action(s, action_from_name[alpha], transitions)

    return mdp


def str_to_float(string: str) -> float:
    q = string.split('/')
    if len(q) > 1:
        return reduce(lambda x, y: float(x) / float(y), string.split('/'))
    else:
        return float(string)
