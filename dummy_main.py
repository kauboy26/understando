from dummy_impl.dummy_system import DummyNode, DummyMessage
from corelib import search
import math

# Create some nodes
addrs = ['node1', 'node2', 'node3']
nodes = [DummyNode(a, addrs) for a in addrs]

# Start off by having a message to each node.
starting_messages = [(DummyMessage({'start_election': 1}), 'client1', a) for a in addrs]
start_state = search.build_start_state_from_raw_materials(starting_messages, nodes)

def single_node_elected(state):
    num_elected = 0
    for addr, node in state.nodes.items():
        if node.am_leader:
            num_elected += 1
    
    return num_elected == 1

states_found, states_examined = search.system_state_BFS(start_state, math.inf, single_node_elected)

print("States examined: ", len(states_examined))

curr = states_found[0]

while curr is not None:
    print(curr)
    curr = curr.previous_state
