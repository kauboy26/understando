from dummy_impl.dummy_system import DummyNode, DummyMessage
from corelib import search

# Create some nodes
addrs = ['node1', 'node2', 'node3']
nodes = [DummyNode(a, addrs) for a in addrs]

# Start off by having a message to each node.
starting_messages = [(DummyMessage({'start_election': 1}), 'client1', a) for a in addrs]

algo = search.SearchAlgorithm(nodes, starting_messages)

def single_node_elected(state):
    num_elected = 0
    for addr, node in state.nodes.items():
        if node.am_leader:
            num_elected += 1
    
    return num_elected == 1

states_found, states_examined = algo.start_search(20, single_node_elected)

curr = states_found[0]

while curr is not None:
    print(curr)
    curr = curr.previous_state
