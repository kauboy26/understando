from paxos_simple.paxos_node import PaxosSimpleAcceptor, PaxosSimpleProposer, PaxosSimpleMessage
from paxos_simple.paxos_node import CLIENT_VALUE
from corelib import search
from corelib.search import print_unlinked_state as ps
import math

import json

# Create some acceptor nodes
acc_nodes = [PaxosSimpleAcceptor(f'acceptor{i}', []) for i in range(3)]
# Create some proposer nodes
prop_nodes = [PaxosSimpleProposer(f'proposer{i}', [acc.addr for acc in acc_nodes], i) for i in range(2)]

# Start off by having a message to each node.
starting_messages = [(PaxosSimpleMessage(CLIENT_VALUE, {"value": p.addr}), 'client1', p.addr) for p in prop_nodes]
start_state = search.build_start_state_from_raw_materials(starting_messages, acc_nodes + prop_nodes)

def value_chosen(state):
    for addr, node in state.nodes.items():
        if isinstance(node, PaxosSimpleProposer) and node.chosen:
            return True
    return False

def should_skip(state):
    return False

states_found, states_examined = search.system_state_BFS(start_state, 15, value_chosen, should_skip)

# The first such state that was found with a chosen value.
curr = states_found[0]
# Print the state:
ps(curr)

# Is it possible for both proposers to have their values chosen?
def find_prop_1(state):
    return state.nodes['proposer1'].chosen

more_states, _ = search.system_state_BFS(curr, 12, find_prop_1, should_skip)
# Apparently there are, since 'more_states' does not have a length of 0.
