"""
This module is used to handle yaml file and more precisely to import MDP from yaml file.
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
            transitions = [(state_from_name[transition['target']],
                            str_to_float(str(transition['probability'])))
                           for transition in enabled_action['transitions']]

            alpha = enabled_action['name']

            # enable this action in the MDP
            mdp.enable_action(s, action_from_name[alpha], transitions)

    return mdp


def export_to_yaml(mdp: MDP, file_name: str) -> None:
    """
    Serialise a MDP instance into a yaml file.

    :param mdp: a MDP
    :param file_name: the name of the yaml file
    """
    mdp_dict = {'mdp': {'states': [], 'actions': []}}
    for s in range(mdp.number_of_states):
        mdp_dict['mdp']['states'].append({})
        mdp_dict['mdp']['states'][-1]['name'] = mdp.state_name(s)
        mdp_dict['mdp']['states'][-1]['enabled actions'] = []
        for (alpha, succ_list) in mdp.alpha_successors(s):
            mdp_dict['mdp']['states'][-1]['enabled actions'].append({})
            mdp_dict['mdp']['states'][-1]['enabled actions'][-1]['name'] = mdp.act_name(alpha)
            mdp_dict['mdp']['states'][-1]['enabled actions'][-1]['transitions'] = []
            for (succ, pr) in succ_list:
                mdp_dict['mdp']['states'][-1]['enabled actions'][-1]['transitions'].append({})
                mdp_dict['mdp']['states'][-1]['enabled actions'][-1]['transitions'][-1]['target'] = mdp.state_name(succ)
                mdp_dict['mdp']['states'][-1]['enabled actions'][-1]['transitions'][-1]['probability'] = pr
    for alpha in range(mdp.number_of_actions):
        mdp_dict['mdp']['actions'].append({})
        mdp_dict['mdp']['actions'][-1]['name'] = mdp.act_name(alpha)
        mdp_dict['mdp']['actions'][-1]['weight'] = mdp.w(alpha)
    if file_name:
        with open(file_name + '.yaml', 'w') as yaml_file:
            yaml.dump(mdp_dict, yaml_file, default_flow_style=False)
    else:
        print(yaml.dump(mdp_dict, default_flow_style=False))


def str_to_float(string: str) -> float:
    """
    Convert a rational number encoded as string into a float.

    :param string: the rational number.
    :return: a float representing the rational number.
    """
    q = string.split('/')
    if len(q) > 1:
        return reduce(lambda x, y: float(x) / float(y), string.split('/'))
    else:
        return float(string)
