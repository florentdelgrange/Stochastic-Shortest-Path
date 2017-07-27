"""
This module is used to manipulate yaml files and more precisely to import MDP from yaml file.
The syntax of yaml that contains MDP is the following :
mdp:
  states:
  - name: <name of a state s>
    enabled actions:
    - name: <name of a enabled action α of s>
      transitions:
      - target: <name of a α-successor of s : s'>
        probability: <∆(s, α, s')>
  actions:
    - name: <name of a action α>
      weight : <w(α)>
"""
from functools import reduce
import yaml
from structures.mdp import MDP


def import_from_yaml(stream) -> MDP:
    """
    Import a yaml file (as stream) into a MDP.

    :param stream: yaml file stream.
    :return: the MDP imported from the yaml file
    """
    mdp_dict = yaml.load(stream)['mdp']
    mdp_states = mdp_dict['states']
    mdp_actions = mdp_dict['actions']
    states = [state['name'] for state in mdp_states]
    state_from_name = {}
    for i in range(len(mdp_states)):
        state_from_name[states[i]] = i
    actions = [action['name'] for action in mdp_actions]
    w = [int(action['weight']) for action in mdp_actions]
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

            # enable this action in the MDP
            mdp.enable_action(s, action_from_name[alpha], transitions)

    return mdp


def str_to_float(string: str) -> float:
    """
    Convert a rational number encoded as string into a float.

    :param string: the rational number.
    :return: a float representing the rational number.
    """
    if string[0] == '-':
        raise RuntimeError(string + " < 0; probabilities must be strictly positive rational numbers.")
    q = string.split('/')
    if len(q) > 1:
        return reduce(lambda x, y: float(x) / float(y), string.split('/'))
    else:
        return float(string)
