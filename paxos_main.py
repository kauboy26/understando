from paxos_simple.paxos_node import PaxosSimpleAcceptor, PaxosSimpleProposer, PaxosSimpleMessage
from paxos_simple.paxos_node import CLIENT_VALUE
from corelib import search
import math

import json

# Create some acceptor nodes
acc_nodes = [PaxosSimpleAcceptor(f'acceptor{i}', []) for i in range(3)]
# Create some proposer nodes
prop_nodes = [PaxosSimpleProposer(f'proposer{i}', [acc.addr for acc in acc_nodes], i) for i in range(1)]

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

states_found, states_examined = search.system_state_BFS(start_state, math.inf, value_chosen, should_skip)

print("States examined: ", len(states_examined))

curr = states_found[0]

print(json.dumps(curr, default=lambda o: o.__dict__, indent=2))
